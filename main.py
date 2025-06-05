from wumpus_world import WumpusWorld
from logic_agent import LogicAgent

def main():
    # Create the Wumpus World environment
    world = WumpusWorld()
    
    print("=== WUMPUS WORLD ===")
    print("Agent starting at (0, 0)")
    print("Initial percepts:", world.percepts)
    
    # Create the logic-based agent
    agent = LogicAgent(world)
    
    # Run the agent in the environment
    agent.run()
    
    # Final game result
    result = world.is_game_over()
    if result == "win":
        print("🏆 The agent grabbed the gold and returned safely. You win!")
    elif result == "lose":
        print("💀 The agent fell into a pit or was eaten by the Wumpus. You lose!")
    else:
        print("❓ The agent stopped without winning or dying.")

if __name__ == "__main__":
    main()
