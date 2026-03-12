import sys
import os

# Add mtg_core to PYTHONPATH so we can run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mtg_core.engine import MTGEngine
from mtg_core.game_state import GameState
from mtg_core.player_state import PlayerState
from mtg_core.ai_pregame import AIPregameDecider, MulliganContext, BottomContext, CardView
from mtg_core.tui_base import TUIPlayer

def main():
    print("Setting up Magic: The Gathering Game...")

    # 1. Initialize Game State
    player1_id = "P1"
    player2_id = "P2"

    players = {
        player1_id: PlayerState(player_id=player1_id, life=20, library=[], hand=[], graveyard=[]),
        player2_id: PlayerState(player_id=player2_id, life=20, library=[], hand=[], graveyard=[])
    }

    game = GameState.new_game(players=players)
    
    # We need a basic deck for these players to play.
    # For now, let's just initialize the engine.
    engine = MTGEngine(game_state=game)

    # 2. Pregame (Mulligans)
    # The AIBroker will start automatically when ResponsesCreateText is called
    pregame_ai = AIPregameDecider(model="gemini-2.5-flash")

    print(f"\n[Pregame] Starting Mulligans for {player1_id} (Human)...")
    while True:
        # Mocking a mulligan context for P1
        ctx1 = MulliganContext(
            player_id=player1_id,
            deck_name="Test Deck 1",
            on_play=True,
            mulligans_taken=game.players[player1_id].mulligans_taken,
            hand=[] # Empty hand for now
        )
        
        print("\nYour hand: [Empty Hand Mock]")
        print(f"Mulligans taken: {ctx1.mulligans_taken}")
        choice = input(f"{player1_id}, do you want to KEEP or MULLIGAN? [k/M]: ").strip().lower()
        if choice in ('k', 'keep'):
            print(f"{player1_id} kept.")
            break
        else:
            print(f"{player1_id} mulliganed.")
            game.players[player1_id].mulligans_taken += 1
            if game.players[player1_id].mulligans_taken >= 7:
                print("Max mulligans reached. Keeping.")
                break

    print(f"\n[Pregame] Starting Mulligans for {player2_id} (AI)...")
    # Mocking a mulligan context for P2
    ctx2 = MulliganContext(
        player_id=player2_id,
        deck_name="Test Deck 2",
        on_play=False,
        mulligans_taken=0,
        hand=[] # Empty hand for now
    )
    
    try:
        decision2 = pregame_ai.decide_mulligan(ctx2)
        print(f"{player2_id} decided to: {decision2.decision}")
        if decision2.reasoning:
            print(f"Reasoning: {decision2.reasoning}")
    except Exception as e:
        print(f"Warning: {player2_id} mulligan failed: {e}")

    # 3. Transition to TUI
    print("\n[Game] Transitioning to Live Game TUI in 3 seconds...")
    import time
    time.sleep(3)

    # We will spin up the TUI for Player 1.
    tui_p1 = TUIPlayer(
        engine=engine,
        player_id=player1_id,
        collect_reasoning=False
    )
    
    # Enter the event loop
    # Note: TUIPlayer.loop() renders the TUI blockingly for one action, 
    # we would probably want to loop it.
    while True:
        try:
            # We just run the loop over and over. If the engine ends the game, tui might quit.
            # But TUI loop exits after 1 action inside choose_action_index_tui.
            tui_p1.loop()
        except Exception as e:
            print(f"Game ended or error: {e}")
            break

if __name__ == "__main__":
    main()
