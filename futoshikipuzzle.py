import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame
from PIL import Image, ImageTk

# Initialize Pygame mixer
pygame.mixer.init()

# Load and play background music
pygame.mixer.music.load("audio2.mp3")
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

class FutoshikiGame:
    def __init__(self, root, size=4, difficulty='easy', adventure_mode=False, duel_mode=False, player=None, player1_time=None, player2_time=None, start_time=None, player1_name="", player2_name=""):
        self.root = root
        self.root.title("Futoshiki Puzzle")
        self.root.state('zoomed')
        self.root.configure(bg='sky blue')
        self.size = size
        self.difficulty = difficulty
        self.adventure_mode = adventure_mode
        self.duel_mode = duel_mode
        self.player = player
        self.player1_time = player1_time
        self.player2_time = player2_time
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.start_time = start_time if start_time is not None else time.time()
        self.timer_running = True

        # Add background image
        try:
            self.bg_image = Image.open("puzzlebg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.entries = {}
        self.inequalities = {}
        self.board = [[0] * self.size for _ in range(self.size)]
        self.original_puzzle = []
        self.generate_solved_board()
        self.generate_puzzle()
        self.create_grid()
        self.create_buttons()
        self.create_timer()
        self.update_timer()

        # Load sound files
        self.valid_sound = pygame.mixer.Sound("audio1.wav")
        self.invalid_sound = pygame.mixer.Sound("invalid.wav")
        self.button_click_sound = pygame.mixer.Sound("button.wav")
        self.congrats_sound = pygame.mixer.Sound("congrats.wav")

        # Display title and puzzle size
        self.display_title()

        # Display the initial message
        self.show_message("Welcome to Futoshiki Puzzle! Fill the grid with numbers according to the rules.")

    def generate_solved_board(self):
        self.board = [[0] * self.size for _ in range(self.size)]
        self.solve_board(self.board)

    def solve_board(self, board):
        for row in range(self.size):
            for col in range(self.size):
                if board[row][col] == 0:
                    nums = list(range(1, self.size + 1))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve_board(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def is_valid(self, board, row, col, num):
        for i in range(self.size):
            if board[row][i] == num or board[i][col] == num:
                return False

        for ((r1, c1), (r2, c2)), sign in self.inequalities.items():
            if (row == r1 and col == c1) or (row == r2 and col == c2):
                if (row == r1 and col == c1) and board[r2][c2] != 0:
                    if sign == '>' and not (num > board[r2][c2]):
                        return False
                    if sign == '<' and not (num < board[r2][c2]):
                        return False
                    if sign == 'v' and not (num > board[r2][c2]):
                        return False
                    if sign == 'ʌ' and not (num < board[r2][c2]):
                        return False
                if (row == r2 and col == c2) and board[r1][c1] != 0:
                    if sign == '>' and not (board[r1][c1] > num):
                        return False
                    if sign == '<' and not (board[r1][c1] < num):
                        return False
                    if sign == 'v' and not (board[r1][c1] > num):
                        return False
                    if sign == 'ʌ' and not (board[r1][c1] < num):
                        return False

        return True

    def generate_puzzle(self):
        if self.difficulty == 'easy':
            num_revealed = self.size * self.size // 2
            num_inequalities = self.size
        elif self.difficulty == 'medium':
            num_revealed = self.size * self.size // 3
            num_inequalities = self.size - 1
        elif self.difficulty == 'hard':
            num_revealed = self.size * self.size // 4
            num_inequalities = self.size - 2

        positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(positions)
        revealed_positions = positions[:num_revealed]

        self.puzzle = [[self.board[i][j] if (i, j) in revealed_positions else 0 for j in range(self.size)] for i in range(self.size)]
        self.original_puzzle = [row[:] for row in self.puzzle]

        for _ in range(num_inequalities):
            row1, col1 = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            direction = random.choice(['horizontal', 'vertical'])
            if direction == 'horizontal' and col1 < self.size - 1:
                row2, col2 = row1, col1 + 1
            elif direction == 'vertical' and row1 < self.size - 1:
                row2, col2 = row1 + 1, col1
            else:
                continue

            if direction == 'horizontal':
                if self.board[row1][col1] > self.board[row2][col2]:
                    sign = '>'
                else:
                    sign = '<'
            elif direction == 'vertical':
                if self.board[row1][col1] > self.board[row2][col2]:
                    sign = 'v'
                else:
                    sign = 'ʌ'

            self.inequalities[((row1, col1), (row2, col2))] = sign

    def create_grid(self):
        validate_cmd = (self.root.register(self.validate_entry), '%P')

        self.frame = tk.Frame(master=self.root, width=500, height=500, bg='lightblue')
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        for i in range(self.size):
            for j in range(self.size):
                value = self.puzzle[i][j]
                entry = tk.Entry(master=self.frame, font=('Arial', 14), width=3, justify='center', borderwidth=2,
                                 validate='key', validatecommand=validate_cmd, bg='white')
                entry.grid(row=i * 2, column=j * 2, padx=5, pady=5, sticky='news')
                entry.bind("<FocusIn>", self.on_focus_in)
                entry.bind("<FocusOut>", self.on_focus_out)
                entry.bind("<KeyRelease>", self.on_key_release)
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state='disabled', disabledbackground='lightgray')
                self.entries[(i, j)] = entry

        for ((row1, col1), (row2, col2)), sign in self.inequalities.items():
            label_row = row1 * 2 if row1 == row2 else min(row1, row2) * 2 + 1
            label_col = col1 * 2 + 1 if col1 != col2 else col1 * 2
            tk.Label(master=self.frame, text=sign, font=('Arial', 14), bg="lightblue").grid(row=label_row, column=label_col)
        for i in range(1, 2 * self.size - 1):
            if i % 2 != 0:
                tk.Label(master=self.frame, text=" ", bg="lightblue").grid(row=0, column=i)
                tk.Label(master=self.frame, text=" ", bg="lightblue").grid(row=i, column=0)

    def display_title(self):
        title_frame = tk.Frame(self.root, bg=self.root.cget('bg'))
        title_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        title_label = tk.Label(title_frame, text="FUTOSHIKI", font=("Arial", 24, "bold"), bg=self.root.cget('bg'))
        title_label.pack()

        size_label = tk.Label(title_frame, text=f"{self.size}x{self.size} Puzzle", font=("Arial", 18), bg=self.root.cget('bg'))
        size_label.pack()

        if self.duel_mode:
            player_label = tk.Label(title_frame, text=f"Player: {self.player}", font=("Arial", 18), bg=self.root.cget('bg'))
            player_label.pack()

    def on_focus_in(self, event):
        event.widget.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)

    def on_focus_out(self, event):
        event.widget.config(highlightbackground="black", highlightcolor="black", highlightthickness=1)

    def on_key_release(self, event):
        if event.keysym in ["BackSpace", "Return"]:
            return
        value = event.widget.get()
        if value.isdigit() and 1 <= int(value) <= self.size:
            self.play_valid_sound()
        else:
            self.play_invalid_sound()

    def play_valid_sound(self):
        self.valid_sound.play()

    def play_invalid_sound(self):
        self.invalid_sound.play()

    def play_button_click_sound(self):
        self.button_click_sound.play()

    def play_congrats_sound(self):
        self.congrats_sound.play()

    def create_buttons(self):
        frame = tk.Frame(self.root, bg=self.root.cget('bg'))
        frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        back_button = tk.Button(self.root, text="Back", command=self.back_button_click, bg='#FF5733', fg='white', font=('Arial', 14), padx=10, pady=5)
        back_button.place(relx=0.3, rely=0.9,anchor=tk.CENTER, width=150, height=50)

        start_over_button = tk.Button(self.root, text="Start Over", command=self.start_over_button_click, bg='#FF5733', fg='white', font=('Arial', 14), padx=10, pady=5)
        start_over_button.place(relx=0.45, rely=0.9,anchor=tk.CENTER, width=150, height=50)

        solve_button = tk.Button(self.root, text="Check Solution", command=self.check_solution_button_click, bg='#FF5733', fg='white', font=('Arial', 14), padx=10, pady=5)
        solve_button.place(relx=0.6, rely=0.9,anchor=tk.CENTER, width=150, height=50)

        new_puzzle_button = tk.Button(self.root, text="New Puzzle", command=self.new_puzzle_button_click, bg='#FF5733', fg='white', font=('Arial', 14), padx=10, pady=5)
        new_puzzle_button.place(relx=0.75, rely=0.9,anchor=tk.CENTER, width=150, height=50)

    def create_timer(self):
        self.timer_label = tk.Label(self.root, text="Time: 00:00", font=('Arial', 14), bg=self.root.cget('bg'))
        self.timer_label.place(relx=0.9, rely=0.05, anchor=tk.CENTER)

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def new_puzzle_button_click(self):
        if self.adventure_mode:
            messagebox.showinfo("New Puzzle", "New puzzle is not allowed. You must start over from 3x3.")
            self.start_over()
        else:
            self.play_button_click_sound()
            self.new_puzzle()

    def start_over_button_click(self):
        self.play_button_click_sound()
        confirm = messagebox.askyesno("Confirm Start Over", "Are you sure you want to start over?")
        if confirm:
            if self.adventure_mode:
                self.start_adventure_from_beginning()
            else:
                self.start_over()

    def check_solution_button_click(self):
        self.play_button_click_sound()
        self.check_solution()

    def back_button_click(self):
        self.play_button_click_sound()
        self.go_back()

    def go_back(self):
        self.root.destroy()
        home_root = tk.Tk()
        HomePage(home_root)
        home_root.state('zoomed')
        home_root.mainloop()

    def new_puzzle(self):
        Playagain(self.root,self.size,self.difficulty)

    def start_over(self):
        self.puzzle = [row[:] for row in self.original_puzzle]
        self.frame.destroy()
        self.create_grid()
        self.start_time = time.time()

    def start_adventure_from_beginning(self):
        self.root.destroy()
        adventure_root = tk.Tk()
        FutoshikiGame(adventure_root, 3, 'easy', adventure_mode=True)
        adventure_root.state('zoomed')
        adventure_root.mainloop()

    def validate_entry(self, P):
        if P == "":
            return True
        if P.isdigit() and 1 <= int(P) <= self.size:
            return True
        return False

    def check_solution(self):
        try:
            board = [[0] * self.size for _ in range(self.size)]
            for (row, col), entry in self.entries.items():
                if entry.get():
                    board[row][col] = int(entry.get())
                else:
                    raise ValueError("Puzzle is incomplete. Please fill all cells.")

            for row in range(self.size):
                if len(set(board[row])) != self.size or len(set(board[i][row] for i in range(self.size))) != self.size:
                    raise ValueError("Duplicate in row or column")

            for ((row1, col1), (row2, col2)), sign in self.inequalities.items():
                if board[row1][col1] != 0 and board[row2][col2] != 0:
                    if sign == '>' and not (board[row1][col1] > board[row2][col2]):
                        raise ValueError(f"Inequality condition not met at {row1, col1} {sign} {row2, col2}")
                    if sign == '<' and not (board[row1][col1] < board[row2][col2]):
                        raise ValueError(f"Inequality condition not met at {row1, col1} {sign} {row2, col2}")
                    if sign == 'v' and not (board[row1][col1] > board[row2][col2]):
                        raise ValueError(f"Inequality condition not met at {row1, col1} {sign} {row2, col2}")
                    if sign == 'ʌ' and not (board[row1][col1] < board[row2][col2]):
                        raise ValueError(f"Inequality condition not met at {row1, col1} {sign} {row2, col2}")

            end_time = time.time()
            elapsed_time = end_time - self.start_time
            self.timer_running = False
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            if self.adventure_mode and self.size < 10:
                self.next_adventure_level()
            elif self.duel_mode:
                self.handle_duel_completion(minutes, seconds)
            else:
                self.show_congratulations(minutes, seconds)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input. Please enter numbers only. ({str(e)})")

    def next_adventure_level(self):
        next_level = self.size + 1
        if next_level > 8:
            self.end_adventure_mode()
        else:
            self.root.destroy()
            next_level_root = tk.Tk()
            FutoshikiGame(next_level_root, next_level, 'easy', adventure_mode=True, start_time=self.start_time)
            next_level_root.state('zoomed')
            next_level_root.mainloop()

    def end_adventure_mode(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.root.destroy()
        
        congrats_root = tk.Tk()
        congrats_root.title("Congratulations!")
        congrats_root.state('zoomed')

        self.root = tk.Tk()
        self.root.withdraw()
        # Add background image
        try:
            self.bg_image = Image.open("celeb.jpg")
            self.bg_image = self.bg_image.resize((congrats_root.winfo_screenwidth(), congrats_root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(congrats_root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        congrats_label = tk.Label(congrats_root, text="Congratulations!", font=("Arial", 24), bg='lightblue')
        congrats_label.pack(pady=20)

        time_label = tk.Label(congrats_root, text=f"You solved 3x3 to 8x8 puzzles in just {minutes:02}:{seconds:02}!", font=("Arial", 18), bg='lightblue')
        time_label.pack(pady=10)

        button_frame = tk.Frame(congrats_root, bg="lightblue")
        button_frame.pack(pady=20)

        home_button = tk.Button(button_frame, text="Home", font=('Arial', 14), command=lambda: self.go_home(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        home_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(button_frame, text="Exit", font=('Arial', 14), command=lambda: self.exit_game(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        exit_button.pack(side=tk.LEFT, padx=10)

    def handle_duel_completion(self, minutes, seconds):
        if self.player == self.player1_name:
            self.player1_time = minutes * 60 + seconds
            self.root.destroy()
            duel_root = tk.Tk()
            PlayerSelectionWindow(duel_root, self.size, self.difficulty, self.player1_time, self.player1_name, self.player2_name)
            duel_root.state('zoomed')
            duel_root.mainloop()
        elif self.player == self.player2_name:
            self.player2_time = minutes * 60 + seconds
            self.show_duel_congratulations()

    def show_duel_congratulations(self):
        winner = self.player1_name if self.player1_time < self.player2_time else self.player2_name
        winner_time = self.player1_time if self.player1_time < self.player2_time else self.player2_time
        minutes = winner_time // 60
        seconds = winner_time % 60

        self.play_congrats_sound()
        congrats_root = tk.Toplevel(self.root)
        congrats_root.title("Congratulations!")
        congrats_root.state('zoomed')
        
        # Add background image
        try:
            self.bg_image = Image.open("celeb.jpg")
            self.bg_image = self.bg_image.resize((congrats_root.winfo_screenwidth(), congrats_root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(congrats_root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")
        
        congrats_label = tk.Label(congrats_root, text="Congratulations!", font=("Arial", 24), bg='lightblue')
        congrats_label.pack(pady=20)

        winner_label = tk.Label(congrats_root, text=f"{winner} wins!", font=("Arial", 24), bg='lightblue')
        winner_label.pack(pady=10)

        time_label = tk.Label(congrats_root, text=f"Winning time: {minutes:02}:{seconds:02}", font=("Arial", 18), bg='lightblue')
        time_label.pack(pady=10)

        button_frame = tk.Frame(congrats_root, bg="lightblue")
        button_frame.pack(pady=20)

        play_again_button = tk.Button(button_frame, text="Play Again", font=('Arial', 14), command=lambda: self.play_again(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        play_again_button.pack(side=tk.LEFT, padx=10)

        home_button = tk.Button(button_frame, text="Home", font=('Arial', 14), command=lambda: self.go_home(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        home_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(button_frame, text="Exit", font=('Arial', 14), command=lambda: self.exit_game(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        exit_button.pack(side=tk.LEFT, padx=10)

    def show_congratulations(self, minutes, seconds):
        self.play_congrats_sound()
        congrats_root = tk.Toplevel(self.root)
        congrats_root.title("Congratulations!")
        congrats_root.state('zoomed')
        
        # Add background image
        try:
            self.bg_image = Image.open("celeb.jpg")
            self.bg_image = self.bg_image.resize((congrats_root.winfo_screenwidth(), congrats_root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(congrats_root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")
        
        congrats_label = tk.Label(congrats_root, text="Congratulations!", font=("Arial", 24), bg='lightblue')
        congrats_label.pack(pady=20)

        time_label = tk.Label(congrats_root, text=f"You solved the puzzle in {minutes:02}:{seconds:02}.", font=("Arial", 18), bg='lightblue')
        time_label.pack(pady=10)

        button_frame = tk.Frame(congrats_root, bg="lightblue")
        button_frame.pack(pady=20)

        play_again_button = tk.Button(button_frame, text="Play Again", font=('Arial', 14), command=lambda: self.play_again(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        play_again_button.pack(side=tk.LEFT, padx=10)

        home_button = tk.Button(button_frame, text="Home", font=('Arial', 14), command=lambda: self.go_home(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        home_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(button_frame, text="Exit", font=('Arial', 14), command=lambda: self.exit_game(congrats_root), bg='#FF5733', fg='white', padx=10, pady=5)
        exit_button.pack(side=tk.LEFT, padx=10)

    def play_again(self, congrats_root):
        self.play_button_click_sound()
        congrats_root.destroy()
        if self.adventure_mode:
            self.start_adventure_from_beginning()
        elif self.duel_mode:
            self.restart_duel_mode()
        else:
            self.new_puzzle()

    def restart_duel_mode(self):
        self.play_button_click_sound()
        self.root.destroy()
        duel_root = tk.Tk()
        DuelModeWindow(duel_root)
        duel_root.state('zoomed')
        duel_root.mainloop()

    def go_home(self, congrats_root):
        self.play_button_click_sound()
        congrats_root.destroy()
        self.go_back()

    def exit_game(self, congrats_root):
        self.play_button_click_sound()
        congrats_root.destroy()
        self.root.destroy()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png") 
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class Playagain:
    def __init__(self,root,size,difficulty):
        self.root = root
        self.size = size
        self.difficulty = difficulty
        FutoshikiGame(self.root,self.size,self.difficulty )

class HomePage:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.configure(bg='sky blue')

        try:
            self.bg_image = Image.open("image1.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.root.title("Welcome Page")

        entry_message = tk.Label(self.root, text="Futoshiki Pro", font=("Stencil", 50), bg=self.root.cget('bg'))
        entry_message.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        start_button = tk.Button(self.root, text="Start", bg="lightpink", font=("Arial", 20), command=self.start_button_click)
        start_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=200, height=50)

        instructions_button = tk.Button(self.root, text="Instructions", bg="lightpink", font=("Arial", 20), command=self.instructions_button_click)
        instructions_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=200, height=50)

        exit_button = tk.Button(self.root, text="Exit", bg="lightpink", font=("Arial", 20), command=self.exit_game)
        exit_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER, width=200, height=50)

        self.create_volume_button()

        # Display the initial message
        self.show_message("Welcome to Futoshiki! Click 'Start' to begin or 'Instructions' for help.")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def start_button_click(self):
        self.play_button_click_sound()
        self.open_mode_selection()

    def instructions_button_click(self):
        self.play_button_click_sound()
        self.inst()

    def exit_game(self):
        self.play_button_click_sound()
        self.root.destroy()

    def inst(self):
        self.root.destroy()
        inst_root = tk.Tk()
        InstructionsWindow(inst_root)
        inst_root.state('zoomed')
        inst_root.mainloop()

    def open_mode_selection(self):
        self.root.destroy()
        mode_selection_root = tk.Tk()
        ModeSelectionWindow(mode_selection_root)
        mode_selection_root.state('zoomed')
        mode_selection_root.mainloop()

    def create_volume_button(self):
        self.volume_button = tk.Button(self.root, text="🔊", font=("Arial", 18), command=self.toggle_volume, bg="lightpink", borderwidth=0)
        self.volume_button.place(relx=0.95, rely=0.95, anchor=tk.CENTER)

    def toggle_volume(self):
        if pygame.mixer.music.get_volume() > 0:
            pygame.mixer.music.set_volume(0)
            self.volume_button.config(text="🔈")
        else:
            pygame.mixer.music.set_volume(1)
            self.volume_button.config(text="🔊")

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  # Replace with the path to your character image
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class ModeSelectionWindow:
    def __init__(self, root):
        
        self.root = root
        self.root.state('zoomed')
        self.root.title("Select Mode")
        self.root.configure(bg='lightblue')

        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        classic_button = tk.Button(self.root, text="Classic", font=("Arial", 24), command=self.classic_mode, bg='lightpink')
        classic_button.place(relx=0.5, rely=0.35, anchor=tk.CENTER, width=200, height=50)

        adventure_button = tk.Button(self.root, text="Adventure", font=("Arial", 24), command=self.adventure_mode, bg='lightpink')
        adventure_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=200, height=50)

        duel_button = tk.Button(self.root, text="Dual", font=("Arial", 24), command=self.duel_mode, bg='lightpink')
        duel_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER, width=200, height=50)

        # Display the initial message
        self.show_message("Select a game mode to start playing!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def classic_mode(self):
        self.play_button_click_sound()
        self.root.destroy()
        classic_root = tk.Tk()
        ClassicModeWindow(classic_root)
        classic_root.state('zoomed')
        classic_root.mainloop()

    def adventure_mode(self):
        self.play_button_click_sound()
        self.root.destroy()
        adventure_root = tk.Tk()
        AdventureModeWindow(adventure_root)
        adventure_root.state('zoomed')
        adventure_root.mainloop()

    def duel_mode(self):
        self.play_button_click_sound()
        self.root.destroy()
        duel_root = tk.Tk()
        DuelModeWindow(duel_root)
        duel_root.state('zoomed')
        duel_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class ClassicModeWindow:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Select Difficulty")
        self.root.configure(bg='lightblue')

        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        easy_button = tk.Button(self.root, text="Easy", font=("Arial", 24), command=lambda: self.select_difficulty('easy'), bg='lightpink')
        easy_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER, width=200, height=50)

        medium_button = tk.Button(self.root, text="Medium", font=("Arial", 24), command=lambda: self.select_difficulty('medium'), bg='lightpink')
        medium_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=200, height=50)

        hard_button = tk.Button(self.root, text="Hard", font=("Arial", 24), command=lambda: self.select_difficulty('hard'), bg='lightpink')
        hard_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=200, height=50)
        
        self.show_message("Select a difficulty level: Easy, Medium, or Hard.")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def select_difficulty(self, difficulty):
        self.play_button_click_sound()
        self.root.destroy()
        input_root = tk.Tk()
        InputWindow(input_root, difficulty)
        input_root.state('zoomed')
        input_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class AdventureModeWindow:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Adventure Mode")
        self.root.configure(bg='lightblue')

        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        level_frame = tk.Frame(self.root, bg="lightblue")
        level_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        levels = ["3x3", "4x4", "5x5", "6x6", "7x7", "8x8"]
        for i, level in enumerate(levels):
            level_button = tk.Button(level_frame, text=level, font=("Arial", 18), command=lambda lvl=level: self.start_level(lvl), bg='lightpink', state=tk.DISABLED if i > 0 else tk.NORMAL)
            level_button.grid(row=i//2, column=i%2, padx=10, pady=10)
            setattr(self, f"level_button_{i}", level_button)
        
        # Display the initial message
        self.show_message("Complete each level to unlock the next. Start with the 3x3 puzzle!")
    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()
    def start_level(self, level):
        self.play_button_click_sound()
        size = int(level[0])
        self.root.destroy()
        puzzle_root = tk.Tk()
        FutoshikiGame(puzzle_root, size, 'easy', adventure_mode=True)  # Start with easy difficulty for adventure
        puzzle_root.state('zoomed')
        puzzle_root.mainloop()

    def enable_next_level(self, current_level):
        level_idx = int(current_level[0])
        if level_idx < 8:
            next_button = getattr(self, f"level_button_{level_idx}")
            next_button.config(state=tk.NORMAL)

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class DuelModeWindow:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Dual Mode")
        self.root.configure(bg='lightblue')

        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        title_label = tk.Label(self.root, text="Dual Mode", font=("Arial", 24), bg='lightblue')
        title_label.pack(pady=20)

        player1_label = tk.Label(self.root, text="Player 1 Name:", font=("Arial", 18), bg='lightblue')
        player1_label.pack(pady=10)
        self.player1_entry = tk.Entry(self.root, font=("Arial", 18))
        self.player1_entry.pack(pady=10)

        player2_label = tk.Label(self.root, text="Player 2 Name:", font=("Arial", 18), bg='lightblue')
        player2_label.pack(pady=10)
        self.player2_entry = tk.Entry(self.root, font=("Arial", 18))
        self.player2_entry.pack(pady=10)

        start_button = tk.Button(self.root, text="Start Dual", font=("Arial", 18), command=self.start_duel, bg='lightpink')
        start_button.pack(pady=20)

        # Display the initial message
        self.show_message("Enter names for both players and click 'Start Dual' to begin!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def start_duel(self):
        self.play_button_click_sound()
        player1_name = self.player1_entry.get()
        player2_name = self.player2_entry.get()

        if not player1_name or not player2_name:
            messagebox.showerror("Error", "Both player names are required.")
            return

        self.root.destroy()
        size_input_root = tk.Tk()
        DuelSizeInputWindow(size_input_root, player1_name, player2_name)
        size_input_root.state('zoomed')
        size_input_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  # Replace with the path to your character image
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class DuelSizeInputWindow:
    def __init__(self, root, player1_name, player2_name):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Futoshiki Dual - Select Size")
        self.root.configure(bg='lightblue')
        self.player1_name = player1_name
        self.player2_name = player2_name

        # Add background image
        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.label = tk.Label(self.root, text="Enter the size of the puzzle (3-8):", font=('Arial', 18), bg='lightblue')
        self.label.pack(pady=20)

        self.entry = tk.Entry(self.root, font=('Arial', 18), width=5, justify='center')
        self.entry.pack(pady=10)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_size, bg='lightpink', font=('Arial', 18))
        self.submit_button.pack(pady=20)

        # Display the initial message
        self.show_message("Enter the puzzle size (3-8) and click 'Submit' to start!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def submit_size(self):
        self.play_button_click_sound()
        try:
            size = int(self.entry.get())
            if size < 3 or size > 8:
                raise ValueError("Size must be between 3 and 8.")
            self.root.destroy()
            player_selection_root = tk.Tk()
            PlayerSelectionWindow(player_selection_root, size, 'easy', player1_name=self.player1_name, player2_name=self.player2_name)
            player_selection_root.state('zoomed')
            player_selection_root.mainloop()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  # Replace with the path to your character image
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class PlayerSelectionWindow:
    def __init__(self, root, size, difficulty, player1_time=None, player1_name="", player2_name=""):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Futoshiki Duel - Select Player")
        self.root.configure(bg='lightblue')
        self.size = size
        self.difficulty = difficulty
        self.player1_time = player1_time
        self.player1_name = player1_name
        self.player2_name = player2_name

        # Add background image
        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.label = tk.Label(self.root, text="Select Player to Play:", font=('Arial', 18), bg='lightblue')
        self.label.pack(pady=20)

        if self.player1_time is None:
            player1_button = tk.Button(self.root, text=f"{self.player1_name}", command=lambda: self.start_game(self.player1_name), bg='lightpink', font=('Arial', 18))
            player1_button.pack(pady=10)
        else:
            player1_button = tk.Button(self.root, text=f"{self.player1_name}", bg='lightgrey', font=('Arial', 18), state=tk.DISABLED)
            player1_button.pack(pady=10)

        if self.player1_time is not None:
            player2_button = tk.Button(self.root, text=f"{self.player2_name}", command=lambda: self.start_game(self.player2_name), bg='lightpink', font=('Arial', 18))
            player2_button.pack(pady=10)
        else:
            player2_button = tk.Button(self.root, text=f"{self.player2_name}", bg='lightgrey', font=('Arial', 18), state=tk.DISABLED)
            player2_button.pack(pady=10)

        # Display the initial message
        self.show_message("Select a player to start their turn!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def start_game(self, player):
        self.play_button_click_sound()
        self.root.destroy()
        puzzle_root = tk.Tk()
        FutoshikiGame(puzzle_root, self.size, self.difficulty, duel_mode=True, player=player, player1_time=self.player1_time, player1_name=self.player1_name, player2_name=self.player2_name)
        puzzle_root.state('zoomed')
        puzzle_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  # Replace with the path to your character image
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class InstructionsWindow:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Instructions")
        self.root.configure(bg="lightblue")

        # Add background image
        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add icon at the top
        try:
            self.icon_image = Image.open("instruc.jpg")
            self.icon_image = self.icon_image.resize((50, 50), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(self.icon_image)
            self.icon_label = tk.Label(self.root, image=self.icon, bg='lightblue')
            self.icon_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add title beside the icon
        title_frame = tk.Frame(self.root, bg='lightblue')
        title_frame.pack(pady=10)
        title_label = tk.Label(title_frame, text="FUTOSHIKI", font=("Arial", 24, "bold"), bg="lightblue")
        title_label.pack(side=tk.LEFT)

        instruc_t = tk.Label(self.root, text="Instructions:", font=('Tw Cen MT Condensed Extra Bold', 40), justify=tk.CENTER, bg='lightblue')
        instruc_t.place(relx=0.2, rely=0.25)

        instructions = ("1. Fill the grid with numbers from 1 to the size of the puzzle.\n"
                        "2. Each number must appear exactly once in each row and column.\n"
                        "3. Follow the inequality signs (>, <, v, ʌ) between cells.\n"
                        "4. Click 'Start Game' to begin.")
        instructions_label = tk.Label(self.root, text=instructions, font=('Calibri', 20), justify=tk.LEFT, bg='lightblue')
        instructions_label.place(relx=0.2, rely=0.4)

        button_frame = tk.Frame(self.root, bg="lightblue")
        button_frame.pack(pady=20)

        start_button = tk.Button(self.root, text="Start Game", font=('Arial', 14), command=self.open_mode_selection, bg='lightpink')
        start_button.place(relx=0.4, rely=0.7, width=150, height=50)

        back_button = tk.Button(self.root, text="Back", font=('Arial', 14), command=self.back_button_click, bg='lightpink')
        back_button.place(relx=0.55, rely=0.7, width=150, height=50)

        # Display the initial message
        self.show_message("Follow the instructions to learn how to play Futoshiki!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()
    def open_mode_selection(self):
        self.root.destroy()
        mode_selection_root = tk.Tk()
        ModeSelectionWindow(mode_selection_root)
        mode_selection_root.state('zoomed')
        mode_selection_root.mainloop()
    def start_game_button_click(self):
        self.play_button_click_sound()
        self.start_game()

    def back_button_click(self):
        self.play_button_click_sound()
        self.go_back()

    def start_game(self):
        self.root.destroy()
        input_root = tk.Tk()
        InputWindow(input_root)
        input_root.state('zoomed')
        input_root.mainloop()

    def go_back(self):
        self.root.destroy()
        home_root = tk.Tk()
        HomePage(home_root)
        home_root.state('zoomed')
        home_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

class InputWindow:
    def __init__(self, root, difficulty='easy'):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Futoshiki Puzzle Size")
        self.root.configure(bg='lightblue')
        self.difficulty = difficulty

        # Add background image
        try:
            self.bg_image = Image.open("instruct_bg.jpg")
            self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(self.root, image=self.bg)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add icon at the top
        try:
            self.icon_image = Image.open("instruc.jpg")
            self.icon_image = self.icon_image.resize((100, 100), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(self.icon_image)
            self.icon_label = tk.Label(self.root, image=self.icon, bg='lightblue')
            self.icon_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add title beside the icon
        title_frame = tk.Frame(self.root, bg='lightblue')
        title_frame.pack(pady=10)
        title_label = tk.Label(title_frame, text="FUTOSHIKI", font=("Arial", 24, "bold"), bg="lightblue")
        title_label.pack(side=tk.LEFT)

        self.label = tk.Label(root, text="Enter the size of the puzzle (3-8):", font=('Arial', 14), bg='lightblue')
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=('Arial', 14), width=5, justify='center')
        self.entry.pack(pady=5)

        self.submit_button = tk.Button(root, text="Submit", command=self.submit_button_click, bg='lightpink')
        self.submit_button.pack(pady=10)

        # Display the initial message
        self.show_message("Enter a puzzle size between 3 and 8 and click 'Submit'!")

    def play_button_click_sound(self):
        pygame.mixer.Sound("button.wav").play()

    def submit_button_click(self):
        self.play_button_click_sound()
        self.submit_size()

    def submit_size(self):
        try:
            size = int(self.entry.get())
            if size < 3 or size > 8:
                raise ValueError("Size must be between 3 and 8.")
            self.root.destroy()
            self.open_futoshiki_game(size)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def open_futoshiki_game(self, size):
        puzzle_root = tk.Tk()
        puzzle_root.state('zoomed')
        FutoshikiGame(puzzle_root, size, self.difficulty)
        puzzle_root.mainloop()

    def show_message(self, message):
        # Create a character circle and message box
        self.message_frame = tk.Frame(self.root, bg="lightblue", bd=1, relief=tk.SOLID)
        self.message_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

        try:
            char_image = Image.open("character.png")  
            char_image = char_image.resize((125, 125), Image.LANCZOS)
            self.char_photo = ImageTk.PhotoImage(char_image)
            char_label = tk.Label(self.message_frame, image=self.char_photo, bg="lightblue")
            char_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading character image: {e}")

        message_label = tk.Label(self.message_frame, text=message, font=("Arial", 16), bg="white", wraplength=500, justify=tk.LEFT)
        message_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Remove the message when the screen is clicked
        self.root.bind("<Button-1>", self.remove_message)

    def remove_message(self, event):
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()
            self.root.unbind("<Button-1>")

root = tk.Tk()
home_page = HomePage(root)
root.state('zoomed')
root.mainloop()