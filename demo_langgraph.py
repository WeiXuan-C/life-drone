#!/usr/bin/env python3
"""
LangGraph 工作流程演示
展示基于状态图的复杂救援任务编排
"""

import sys
import time
from agent.reasoning import RescueAgent
from agent.langgraph_workflow import LangGraphRescueWorkflow


def main():
    """LangGraph 演示主程序"""
    
    print("🚁 LangGraph 救援工作流程演示")
    print("=" * 50)
    print("🔄 基于状态图的智能任务编排")
    print("🧠 多阶段推理和决策流程")
    print("🛠️  集成 MCP 工具调用")
    print("📊 实时状态监控和调整")
    
    print("\n🎯 演示场景：")
    print("   1. 地震灾区幸存者搜救")
    print("   2. 洪水区域紧急救援") 
    print("   3. 山区失踪人员搜索")
    print("   4. 自定义救援任务")
    
    choice = input("\n选择演示场景 (1-4): ").strip()
    
    # 定义演示场景
    scenarios = {
        "1": {
            "name": "地震灾区幸存者搜救",
            "goal": "在地震灾区系统性搜索幸存者，优先救援被困人员，确保无人机安全运行",
            "description": "模拟大规模地震后的搜救行动，需要协调多架无人机进行区域覆盖"
        },
        "2": {
            "name": "洪水区域紧急救援", 
            "goal": "在洪水灾区快速定位被困人员，协调救援资源，避开危险水域",
            "description": "洪水环境下的紧急救援，需要考虑水位变化和救援路径"
        },
        "3": {
            "name": "山区失踪人员搜索",
            "goal": "在复杂山地地形中搜索失踪登山者，利用热成像技术定位目标",
            "description": "山区搜救任务，地形复杂，需要精确的路径规划"
        },
        "4": {
            "name": "自定义救援任务",
            "goal": "",
            "description": "用户自定义的救援场景"
        }
    }
    
    if choice in scenarios:
        scenario = scenarios[choice]
        
        if choice == "4":
            scenario["goal"] = input("请输入自定义任务目标: ").strip()
            if not scenario["goal"]:
                scenario["goal"] = "执行标准搜救任务"
        
        print(f"\n🎯 选择场景：{scenario['name']}")
        print(f"📋 任务目标：{scenario['goal']}")
        print(f"📝 场景描述：{scenario['description']}")
        
        # 选择执行模式
        print("\n🔧 选择执行模式：")
        print("1. 🚀 LangGraph 工作流程 (推荐)")
        print("2. 🔄 基础 ReAct 推理")
        print("3. 📊 对比两种模式")
        
        mode_choice = input("选择模式 (1-3): ").strip()
        
        if mode_choice == "1":
            run_langgraph_demo(scenario)
        elif mode_choice == "2":
            run_basic_demo(scenario)
        elif mode_choice == "3":
            run_comparison_demo(scenario)
        else:
            print("❌ 无效选择，使用默认 LangGraph 模式")
            run_langgraph_demo(scenario)
    
    else:
        print("❌ 无效选择，使用默认场景")
        default_scenario = scenarios["1"]
        run_langgraph_demo(default_scenario)


def run_langgraph_demo(scenario: dict):
    """运行 LangGraph 工作流程演示"""
    
    print(f"\n🚀 启动 LangGraph 工作流程演示")
    print("=" * 40)
    
    try:
        # 创建 LangGraph 工作流程
        workflow = LangGraphRescueWorkflow()
        
        print("✅ LangGraph 工作流程初始化成功")
        print("🔄 开始执行状态图工作流程...")
        
        # 执行任务
        start_time = time.time()
        result = workflow.run_mission(scenario["goal"])
        execution_time = time.time() - start_time
        
        # 显示结果
        print(f"\n📊 LangGraph 执行结果：")
        print(f"⏱️  执行时间：{execution_time:.2f} 秒")
        print(f"✅ 任务状态：{'成功' if result['success'] else '失败'}")
        
        if result["success"]:
            print(f"🆘 发现幸存者：{len(result['survivors_found'])} 人")
            print(f"📋 执行步骤：{len(result['messages'])} 个")
            
            print(f"\n🔍 详细执行过程：")
            for i, message in enumerate(result["messages"], 1):
                print(f"   {i}. {message}")
            
            if result["survivors_found"]:
                print(f"\n👥 幸存者位置：")
                for i, survivor in enumerate(result["survivors_found"], 1):
                    pos = survivor["position"]
                    drone = survivor["drone_id"]
                    print(f"   {i}. 位置 ({pos[0]}, {pos[1]}) - 发现者：{drone}")
        
        else:
            print(f"❌ 执行失败：{result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"❌ LangGraph 演示失败：{e}")
        print("💡 请检查依赖项是否正确安装")


def run_basic_demo(scenario: dict):
    """运行基础 ReAct 推理演示"""
    
    print(f"\n🔄 启动基础 ReAct 推理演示")
    print("=" * 40)
    
    try:
        # 创建基础推理代理
        agent = RescueAgent(use_langgraph=False)
        
        print("✅ 基础推理引擎初始化成功")
        print("🧠 开始 ReAct 推理循环...")
        
        # 执行推理循环
        start_time = time.time()
        result = agent.execute_reasoning_cycle(scenario["goal"], use_langgraph=False)
        execution_time = time.time() - start_time
        
        # 显示结果
        print(f"\n📊 基础推理执行结果：")
        print(f"⏱️  执行时间：{execution_time:.2f} 秒")
        print(f"✅ 任务状态：{'成功' if result['success'] else '失败'}")
        
        print(f"\n🧠 推理过程：")
        print(f"💭 思考：{result['thought']}")
        print(f"🎯 行动：{result['action']}")
        print(f"👁️ 观察：{result['observation']}")
        print(f"🤔 反思：{result['reflection']}")
    
    except Exception as e:
        print(f"❌ 基础推理演示失败：{e}")


def run_comparison_demo(scenario: dict):
    """运行两种模式的对比演示"""
    
    print(f"\n📊 启动对比演示")
    print("=" * 40)
    print("🔄 将分别运行 LangGraph 和基础推理模式")
    
    # 运行 LangGraph 模式
    print(f"\n1️⃣ LangGraph 工作流程模式：")
    print("-" * 30)
    run_langgraph_demo(scenario)
    
    print(f"\n" + "=" * 50)
    input("按回车键继续基础推理模式演示...")
    
    # 运行基础推理模式
    print(f"\n2️⃣ 基础 ReAct 推理模式：")
    print("-" * 30)
    run_basic_demo(scenario)
    
    # 对比总结
    print(f"\n📈 模式对比总结：")
    print("=" * 30)
    print("🚀 LangGraph 工作流程：")
    print("   ✅ 多阶段状态管理")
    print("   ✅ 复杂决策流程")
    print("   ✅ 自动状态转换")
    print("   ✅ 更好的任务编排")
    
    print("\n🔄 基础 ReAct 推理：")
    print("   ✅ 简单直接")
    print("   ✅ 快速响应")
    print("   ✅ 资源占用少")
    print("   ⚠️  功能相对有限")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
    except Exception as e:
        print(f"\n❌ 演示出错：{e}")
    
    print("\n🚁 感谢使用 LangGraph 救援系统演示！")