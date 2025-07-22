---
categories:
  - Meachine Learning
tags:
  - LLM
  - RL
mathjax: "true"
title: OpenRLHF框架解读
date: 2025-07-22 11:16:09
---
今天起，笔者会开始尝试更新OpenRLHF的框架解读。主要目的是，让大家能够快速了解训练流程的各个代码的位置。方便大家魔改训练流程，奖励函数以及算法实现。  

我将以`/openrlhf/examples/scripts/train_grpo_ray_hybrid_engine.sh`这个文件作为训练的入口一步步往下剖析  

首先是整个训练的开始，`openrlhf.cli.train_ppo_ray.py`这个文件  
这个文件中的核心就是`train`函数，如下所示  
```python  
def train(args):  

# initialize ray if not initialized  

if not ray.is_initialized():  

ray.init(runtime_env={"env_vars": {"TOKENIZERS_PARALLELISM": "true", "NCCL_DEBUG": "WARN"}})  

  

# configure strategy  

strategy = get_strategy(args)  

strategy.print(args)  

  

# init vllm / actor /critic /ref /reward model  

# if colocated, create placement group for actor and ref model explicitly.  

pg = None  

if args.colocate_actor_ref or args.colocate_all_models:  

if args.init_kl_coef > 0:  

assert (  

args.actor_num_nodes == args.ref_num_nodes  

and args.actor_num_gpus_per_node == args.ref_num_gpus_per_node  

), f"num_nodes and num_gpus_per_node must be the same when colocate actor and ref model."  

  

bundles = [{"GPU": 1, "CPU": 1} for _ in range(args.actor_num_nodes * args.actor_num_gpus_per_node)]  

pg = placement_group(bundles, strategy="PACK")  

ray.get(pg.ready())  

  

# init vLLM engine for text generation  

vllm_engines = None  

if args.vllm_num_engines is not None and args.vllm_num_engines > 0:  

max_len = args.max_len if args.max_len else args.prompt_max_len + args.generate_max_len  

if args.colocate_all_models and not args.async_train:  

assert (  

args.actor_num_nodes * args.actor_num_gpus_per_node  

== args.vllm_num_engines * args.vllm_tensor_parallel_size  

), (  

f"actor_num_nodes * actor_num_gpus_per_node must be equal to "  

f"vllm_num_engines * vllm_tensor_parallel_size, got {args.actor_num_nodes * args.actor_num_gpus_per_node} "  

f"and {args.vllm_num_engines * args.vllm_tensor_parallel_size}"  

)  

  

if args.agent_func_path:  

from openrlhf.trainer.ray.vllm_engine_async import LLMRayActorAsync as LLMRayActor  

else:  

from openrlhf.trainer.ray.vllm_engine import LLMRayActor  

  

vllm_engines = create_vllm_engines(  

args.vllm_num_engines,  

args.vllm_tensor_parallel_size,  

args.pretrain,  

args.seed,  

args.full_determinism,  

args.enable_prefix_caching,  

args.enforce_eager,  

max_len,  

pg if args.colocate_all_models and not args.async_train else None,  

args.vllm_gpu_memory_utilization,  

args.vllm_enable_sleep,  

LLMRayActor,  

args.agent_func_path,  

)  

  

actor_model = RayActorGroup(  

args.actor_num_nodes,  

args.actor_num_gpus_per_node,  

PolicyModelActor,  

pg=pg,  

num_gpus_per_actor=0.2 if pg else 1,  

duplicate_actors=args.ring_attn_size * args.ds_tensor_parallel_size,  

)  

  

if args.init_kl_coef <= 0:  

ref_model = None  

else:  

ref_model = RayActorGroup(  

args.ref_num_nodes,  

args.ref_num_gpus_per_node,  

ReferenceModelActor,  

pg=pg,  

num_gpus_per_actor=0.2 if pg else 1,  

duplicate_actors=args.ring_attn_size * args.ds_tensor_parallel_size,  

)  

  

if not args.colocate_all_models:  

pg = None  

  

# if colocated, create placement group for critic and reward model explicitly.  

if args.critic_pretrain and args.colocate_critic_reward:  

assert (  

args.critic_num_nodes == args.reward_num_nodes  

and args.critic_num_gpus_per_node == args.reward_num_gpus_per_node  

), f"num_nodes and num_gpus_per_node must be the same when colocate critic and reward model."  

  

bundles = [{"GPU": 1, "CPU": 1} for _ in range(args.critic_num_nodes * args.critic_num_gpus_per_node)]  

pg = placement_group(bundles, strategy="PACK")  

ray.get(pg.ready())  

  

if args.critic_pretrain:  

critic_model = RayActorGroup(  

args.critic_num_nodes,  

args.critic_num_gpus_per_node,  

CriticModelActor,  

pg=pg,  

num_gpus_per_actor=0.2 if pg else 1,  

duplicate_actors=args.ring_attn_size * args.ds_tensor_parallel_size,  

)  

else:  

critic_model = None  

  

# multiple reward models  

if not args.remote_rm_url:  

reward_pretrain = args.reward_pretrain  

reward_model = RayActorGroup(  

args.reward_num_nodes,  

args.reward_num_gpus_per_node,  

RewardModelActor,  

pg=pg,  

num_gpus_per_actor=0.2 if pg else 1,  

duplicate_actors=args.ring_attn_size * args.ds_tensor_parallel_size,  

)  

else:  

reward_model = None  

  

if args.async_train:  

from openrlhf.trainer.ppo_trainer_async import PPOTrainerAsync as PPOTrainer  

else:  

from openrlhf.trainer.ppo_trainer import PPOTrainer  

  

# init PPO trainer (Single controller)  

ppo_trainer = PPOTrainer.remote(  

args.pretrain,  

strategy,  

actor_model,  

critic_model,  

reward_model,  

ref_model,  

vllm_engines,  

prompt_split=args.prompt_split,  

eval_split=args.eval_split,  

# generate kwargs  

do_sample=True,  

prompt_max_len=args.prompt_max_len,  

max_new_tokens=args.generate_max_len,  

max_length=args.max_len,  

temperature=args.temperature,  

top_p=args.top_p,  

)  

# training update steps  

max_steps = ray.get(ppo_trainer.get_max_steps.remote())  

  

# init reference/reward/actor model  

refs = []  

if ref_model is not None:  

refs.extend(ref_model.async_init_model_from_pretrained(strategy, args.pretrain))  

refs.extend(actor_model.async_init_model_from_pretrained(strategy, args.pretrain, max_steps, vllm_engines))  

if not args.remote_rm_url:  

refs.extend(reward_model.async_init_model_from_pretrained(strategy, reward_pretrain))  

ray.get(refs)  

  

if args.critic_pretrain:  

# critic scheduler initialization depends on max_step, so we have to init critic after actor  

# TODO: use first reward model as critic model  

refs.extend(critic_model.async_init_model_from_pretrained(strategy, args.critic_pretrain, max_steps))  

ray.get(refs)  

  

# train actor and critic model  

ray.get(ppo_trainer.fit.remote())  

  

# save model  

ray.get(actor_model.async_save_model())  

  

if args.critic_pretrain and args.save_value_network:  

ray.get(critic_model.async_save_model())  
```  