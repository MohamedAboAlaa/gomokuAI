from gui.interface import *
from source.AI import *
from gui.button import Button
import source.utils as utils
import source.gomoku as gomoku
import pygame
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Game initializer function
# Link interface with gomoku moves and AI
# Script to be run


pygame.init()

def ensure_analysis_dir():
    """Ensure the analysis directory exists"""
    if not os.path.exists("analysis"):
        os.makedirs("analysis")
    if not os.path.exists("analysis/game_sim"):
        os.makedirs("analysis/game_sim")

def create_time_heatmap(move_times_array, filename, title):
    """Create a heatmap of move times"""
    ensure_analysis_dir()
    plt.figure(figsize=(10, 8))
    heatmap = plt.imshow(move_times_array, cmap='viridis')
    plt.colorbar(heatmap, label='Time (seconds)')
    plt.title(title)
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.xticks(range(15))
    plt.yticks(range(15))
    plt.savefig(os.path.join("analysis", filename))
    plt.close()

def create_move_time_graph(move_times, filename, title):
    """Create a line graph of move times"""
    ensure_analysis_dir()
    plt.figure(figsize=(12, 6))
    plt.bar(range(1, len(move_times) + 1), move_times)
    plt.title(title)
    plt.xlabel('Move Number')
    plt.ylabel('Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(os.path.join("analysis", filename))
    plt.close()

def create_game_stage_comparison(ai_move_times, filename):
    """Create a bar chart comparing move times across game stages"""
    ensure_analysis_dir()
    
    if len(ai_move_times) < 3:
        return  # Not enough moves to analyze
    
    # Divide the game into early, mid, and late stages
    early_end = min(5, len(ai_move_times) // 3)
    mid_end = min(early_end + len(ai_move_times) // 3, len(ai_move_times))
    
    early_times = ai_move_times[:early_end]
    mid_times = ai_move_times[early_end:mid_end]
    late_times = ai_move_times[mid_end:]
    
    avg_times = [np.mean(early_times) if early_times else 0, 
                np.mean(mid_times) if mid_times else 0, 
                np.mean(late_times) if late_times else 0]
    
    max_times = [np.max(early_times) if early_times else 0, 
                np.max(mid_times) if mid_times else 0, 
                np.max(late_times) if late_times else 0]
    
    stages = ['Early Game', 'Mid Game', 'Late Game']
    x = np.arange(len(stages))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, avg_times, width, label='Average Time')
    ax.bar(x + width/2, max_times, width, label='Maximum Time')
    
    ax.set_ylabel('Time (seconds)')
    ax.set_title('AI Move Times by Game Stage')
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.savefig(os.path.join("analysis", filename))
    plt.close()

def create_game_animation(total_moves):
    """Create an animated GIF from the game screenshots"""
    try:
        from PIL import Image
        import glob
        
        # Get all screenshot files
        screenshot_files = sorted(glob.glob("analysis/game_sim/move_*.png"))
        
        if not screenshot_files:
            print("No screenshots found to create animation")
            return
        
        # Load images
        images = [Image.open(file) for file in screenshot_files]
        
        # Save as GIF
        images[0].save("analysis/game_animation.gif",
                      save_all=True,
                      append_images=images[1:],
                      optimize=False,
                      duration=1000,  # 1 second per frame
                      loop=0)
        
        print("Game animation saved as 'analysis/game_animation.gif'")
    except ImportError:
        print("PIL (Pillow) library not installed. Game animation not created.")
    except Exception as e:
        print(f"Error creating game animation: {e}")

def generate_all_analytics(move_time_data, player_moves, ai_times):
    """Generate all analytics at the end of the game"""
    # Create move time heatmap
    ai_heatmap = np.zeros((15, 15))
    human_heatmap = np.zeros((15, 15))
    move_heatmap = np.zeros((15, 15))
    
    for pos, (time_taken, player) in move_time_data.items():
        i, j = pos
        move_heatmap[i][j] = time_taken
        if player == 1:  # AI
            ai_heatmap[i][j] = time_taken
        else:  # Human
            human_heatmap[i][j] = time_taken
    
    # Create AI move time heatmap
    create_time_heatmap(
        ai_heatmap, 
        "ai_move_time_heatmap.png", 
        "AI Move Times by Board Position"
    )
    
    # Create human move time heatmap
    create_time_heatmap(
        human_heatmap,
        "human_move_time_heatmap.png",
        "Human Move Times by Board Position"
    )
    
    # Create combined player heatmap
    create_time_heatmap(
        move_heatmap, 
        "all_moves_time_heatmap.png", 
        "Move Times by Board Position (AI and Human)"
    )
    
    # Create AI move time graph
    create_move_time_graph(
        ai_times, 
        "ai_move_time_graph.png", 
        "AI Move Time per Move"
    )
    
    # Create game stage comparison
    create_game_stage_comparison(
        ai_times, 
        "game_stage_comparison.png"
    )
    
    # Create game animation from screenshots
    create_game_animation(len(player_moves))
    
    print("Game analytics saved to the 'analysis' directory")

def save_board_screenshot(game, move_number):
    """Save a screenshot of the current board state"""
    ensure_analysis_dir()
    # Pad move number with zeros for correct sorting (001, 002, etc.)
    filename = f"analysis/game_sim/move_{move_number:03d}.png"
    # Save the current screen as an image
    pygame.image.save(game.screen, filename)
    print(f"Saved board state after move {move_number}")

def startGame():
    pygame.init()
    # Initializations
    ai = GomokuAI()
    game = GameUI(ai)
    button_black = Button(game.buttonSurf, 200, 290, "BLACK", 22)
    button_white = Button(game.buttonSurf, 340, 290, "WHITE", 22)

    # Analytics data structures
    move_time_data = {}  # {(i,j): (time_taken, player)} where player is 1 for AI, -1 for human
    player_moves = []    # List of (i, j) positions for all moves
    ai_times = []        # List of AI move times

    # Draw the starting menu
    game.drawMenu()
    game.drawButtons(button_black, button_white, game.screen)
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN\
                    and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                # Check which color the user has chosen and set the states
                game.checkColorChoice(button_black, button_white, mouse_pos)
                game.screen.blit(game.board, (0,0))
                pygame.display.update()
                
                if game.ai.turn == 1:
                    # Measure AI's first move time
                    start_time = time.time()
                    game.ai.firstMove()
                    end_time = time.time()
                    ai_time = end_time - start_time
                    
                    # Record the move
                    move_time_data[(game.ai.currentI, game.ai.currentJ)] = (ai_time, 1)
                    player_moves.append((game.ai.currentI, game.ai.currentJ))
                    ai_times.append(ai_time)
                    
                    game.drawPiece('black', game.ai.currentI, game.ai.currentJ)
                    pygame.display.update()
                    game.ai.turn *= -1
                
                main(game, move_time_data, player_moves, ai_times)

                # When the game ends and there is a winner, draw the result board
                if game.ai.checkResult() != None:
                    # Save final board state
                    save_board_screenshot(game, len(player_moves) + 1)
                    
                    # Generate analytics before showing the result
                    generate_all_analytics(move_time_data, player_moves, ai_times)
                    
                    last_screen = game.screen.copy()
                    game.screen.blit(last_screen, (0,0))
                    # endMenu(game, last_screen)
                    game.drawResult()

                    # Setting for asking to the player to restart the game or not 
                    yes_button = Button(game.buttonSurf, 200, 155, "YES", 18)
                    no_button = Button(game.buttonSurf, 350, 155, "NO", 18)
                    game.drawButtons(yes_button, no_button, game.screen)
                    mouse_pos = pygame.mouse.get_pos()
                    if yes_button.rect.collidepoint(mouse_pos):
                        # Restart the game
                        game.screen.blit(game.board, (0,0))
                        pygame.display.update()
                        game.ai.turn = 0
                        startGame()
                    if no_button.rect.collidepoint(mouse_pos):
                        # End the game
                        pygame.quit()
        pygame.display.update()   

    pygame.quit()

def endMenu(game, last_screen):
    pygame.init()
    game.screen.blit(last_screen, (0,0))
    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            game.drawResult()
            yes_button = Button(game.buttonSurf, 200, 155, "YES", 18)
            no_button = Button(game.buttonSurf, 350, 155, "NO", 18)
            game.drawButtons(yes_button, no_button, game.screen)
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN\
                    and pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                if yes_button.rect.collidepoint(mouse_pos):
                    print('Selected YES')
                    game.screen.blit(game.board, (0,0))
                    pygame.display.update()
                    startGame()
                if no_button.rect.collidepoint(mouse_pos):
                    print('Selected NO')
                    run = False
    pygame.quit()


### Main game play loop ###
def main(game, move_time_data, player_moves, ai_times):
    pygame.init()
    end = False
    result = game.ai.checkResult()
    move_number = 0

    # Save initial board state
    save_board_screenshot(game, move_number)
    
    while not end:
        turn = game.ai.turn
        color = game.colorState[turn] # black or white depending on player's choice
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            # AI's turn
            if turn == 1:
                # Measure AI move time
                start_time = time.time()
                move_i, move_j = gomoku.ai_move(game.ai)
                end_time = time.time()
                ai_time = end_time - start_time
                
                # Record the move
                move_time_data[(move_i, move_j)] = (ai_time, 1)
                player_moves.append((move_i, move_j))
                ai_times.append(ai_time)
                
                # Make the move and update zobrist hash
                game.ai.setState(move_i, move_j, turn)
                game.ai.rollingHash ^= game.ai.zobristTable[move_i][move_j][0]
                game.ai.emptyCells -= 1

                game.drawPiece(color, move_i, move_j)
                
                # Increment move number and save screenshot
                move_number += 1
                save_board_screenshot(game, move_number)
                
                result = game.ai.checkResult()
                # Switch turn
                game.ai.turn *= -1
                print("AI's Turn")
                print(game.ai.nextBound)

            # Human's turn
            if turn == -1:
                if event.type == pygame.MOUSEBUTTONDOWN\
                        and pygame.mouse.get_pressed()[0]:
                    # Measure human move time
                    human_start_time = time.time()
                    
                    # Get human move played
                    mouse_pos = pygame.mouse.get_pos()
                    human_move = utils.pos_pixel2map(mouse_pos[0], mouse_pos[1])
                    move_i = human_move[0]
                    move_j = human_move[1]
                    # print(mouse_pos, move_i, move_j)

                    # Check the validity of human's move
                    if game.ai.isValid(move_i, move_j):
                        human_end_time = time.time()
                        human_time = human_end_time - human_start_time
                        
                        # Record the move
                        move_time_data[(move_i, move_j)] = (human_time, -1)
                        player_moves.append((move_i, move_j))
                        
                        # game.ai.boardValue = game.ai.evaluate(move_i, move_j, game.ai.boardValue, -1, game.ai.nextBound)
                        game.ai.updateBound(move_i, move_j, game.ai.nextBound)
                        game.ai.boardValue = game.ai.evaluate(move_i, move_j, game.ai.boardValue, -1, game.ai.nextBound)
                        game.ai.currentI, game.ai.currentJ = move_i, move_j
                        # Make the move and update zobrist hash
                        game.ai.setState(move_i, move_j, turn)
                        game.ai.rollingHash ^= game.ai.zobristTable[move_i][move_j][1]
                        game.ai.emptyCells -= 1
                        
                        game.drawPiece(color, move_i, move_j)
                        
                        # Increment move number and save screenshot
                        move_number += 1
                        save_board_screenshot(game, move_number)
                        
                        result =  game.ai.checkResult()
                        game.ai.turn *= -1
                        print("Human's Turn")
                        print(game.ai.nextBound)

            
            if result != None:
                # End game
                end = True



if __name__ == '__main__':
    startGame()