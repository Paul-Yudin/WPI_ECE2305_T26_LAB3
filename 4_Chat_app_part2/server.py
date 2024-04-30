import ctypes
import ctypes.wintypes
import win32gui
import win32con
import math
import msvcrt
import socket
import select

global INPUT_NAME  #The name of the input
global INPUT_VALUE #The value of the input
global INPUT_ROW   #The row at which the input is located
global TERM_WIDTH  #The width of the terminal in cols
global TERM_HEIGHT #The height of the terminal in rows

global STOP_WORDS
global HOST
global PORT
global ADDR

global SERVER_SOCKET
global CLIENT_CONNECTION
global CLIENT_ADDR

def move_terminal_cursor(x, y):
    #https://learn.microsoft.com/en-us/windows/console/getstdhandle
    handle = ctypes.windll.kernel32.GetStdHandle(-11)

    #https://learn.microsoft.com/en-us/windows/console/setconsolecursorposition
    cord = ctypes.wintypes._COORD(x, y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(handle, cord)

def get_terminal_info():
    #https://learn.microsoft.com/en-us/windows/console/getstdhandle
    handle = ctypes.windll.kernel32.GetStdHandle(-11)

    #https://learn.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo
    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.wintypes._COORD),
                    ("dwCursorPosition", ctypes.wintypes._COORD),
                    ("wAttributes", ctypes.c_ushort),
                    ("srWindow", ctypes.wintypes.SMALL_RECT),
                    ("dwMaximumWindowSize", ctypes.wintypes._COORD)]
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
    return csbi

def get_terminal_cursor_position():
    csbi = get_terminal_info()
    return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y

def set_terminal_size(columns, lines):
    #https://learn.microsoft.com/en-us/windows/console/getstdhandle
    handle = ctypes.windll.kernel32.GetStdHandle(-11)

    #https://learn.microsoft.com/en-us/windows/console/setconsolewindowinfo
    lpConsoleWindow = ctypes.wintypes.SMALL_RECT(0, 0, columns - 1, lines - 1)
    ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(lpConsoleWindow))
    
    #https://learn.microsoft.com/en-us/windows/console/setconsolescreenbuffersize
    dwSize = ctypes.wintypes._COORD(columns, 9001)
    ctypes.windll.kernel32.SetConsoleScreenBufferSize(handle, dwSize)

    #https://learn.microsoft.com/en-us/windows/console/setconsolewindowinfo
    lpConsoleWindow = ctypes.wintypes.SMALL_RECT(0, 0, columns - 1, lines - 1)
    ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(lpConsoleWindow))
    
def disable_terminal_resize():
    #https://learn.microsoft.com/en-us/windows/console/getconsolewindow
    hWnd = ctypes.windll.kernel32.GetConsoleWindow()

    #https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowlonga
    nIndex = win32con.GWL_STYLE
    current_style = win32gui.GetWindowLong(hWnd, nIndex)

    #https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlonga
    new_style = current_style & ~win32con.WS_SIZEBOX
    win32gui.SetWindowLong(hWnd, nIndex, new_style)

def enable_terminal_resize():
    #https://learn.microsoft.com/en-us/windows/console/getconsolewindow
    hWnd = ctypes.windll.kernel32.GetConsoleWindow()

    #https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowlonga
    nIndex = win32con.GWL_STYLE
    current_style = win32gui.GetWindowLong(hWnd, nIndex)

    #https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlonga
    new_style = current_style | win32con.WS_SIZEBOX
    win32gui.SetWindowLong(hWnd, nIndex, new_style)

def append_msg(new_msg):
    global INPUT_VALUE
    global INPUT_NAME
    global INPUT_ROW
    global TERM_WIDTH

    previous_input_row = INPUT_ROW #Store cursor and input row
    previous_cursor_pos = get_terminal_cursor_position()
    
    move_terminal_cursor(0, INPUT_ROW) #Clear line
    print(" "*TERM_WIDTH)
    
    move_terminal_cursor(0, INPUT_ROW) #Add message
    print(new_msg)
    
    INPUT_ROW = get_terminal_cursor_position()[1] #Shift input down
    print(INPUT_NAME+INPUT_VALUE, end="", flush=True)
    
    move_terminal_cursor(previous_cursor_pos[0], previous_cursor_pos[1]+INPUT_ROW-previous_input_row) #Move cursor

def move_cursor_left():
    global INPUT_NAME
    global INPUT_ROW
    global TERM_WIDTH

    cursor_pos_x, cursor_pos_y = get_terminal_cursor_position()

    first_row = INPUT_ROW
    first_col = len(INPUT_NAME)
    
    if cursor_pos_x==first_col and cursor_pos_y==first_row:
        return 0
    else:
        if cursor_pos_x==0:
            move_terminal_cursor(TERM_WIDTH-1, cursor_pos_y-1) #Move up one row
        else:
            move_terminal_cursor(cursor_pos_x-1, cursor_pos_y) #Move left
        return 1

def move_cursor_right():
    global INPUT_VALUE
    global INPUT_NAME
    global INPUT_ROW
    global TERM_WIDTH

    cursor_pos_x, cursor_pos_y = get_terminal_cursor_position()

    last_row = INPUT_ROW + math.ceil(len(INPUT_NAME+INPUT_VALUE)/TERM_WIDTH) - 1
    last_col = len(INPUT_NAME+INPUT_VALUE)%TERM_WIDTH

    if last_col==0 and len(INPUT_NAME+INPUT_VALUE)!=0:
        last_row +=1

    if cursor_pos_x==last_col and cursor_pos_y==last_row:
        return 0
    else:
        if cursor_pos_x==TERM_WIDTH-1:
            move_terminal_cursor(0, cursor_pos_y+1) #Move down one row
        else:
            move_terminal_cursor(cursor_pos_x+1, cursor_pos_y) #Move right
        return 1

def get_cursor_input_index():
    global INPUT_NAME
    global INPUT_ROW
    global TERM_WIDTH
    
    cursor_pos_x, cursor_pos_y = get_terminal_cursor_position()
    input_cursor_index = (cursor_pos_y-INPUT_ROW)*TERM_WIDTH + cursor_pos_x - len(INPUT_NAME)
    return input_cursor_index

def handle_input():
    global INPUT_VALUE
    global INPUT_NAME
    global INPUT_ROW
    global TERM_WIDTH

    if msvcrt.kbhit():
        key = msvcrt.getch() #Get key code

        if key == b'\xe0' or key == b'\x00': #Detect if key is special function
            key = msvcrt.getch() #Get second part of key code

            if key == b'\x4B': #If left arrow key
                move_cursor_left()
                
            if key == b'\x4D': #If right arrow key
                move_cursor_right()

        else:
            input_cursor_index = get_cursor_input_index()
            
            if key == b'\r': #If enter key
                next_row = INPUT_ROW + math.ceil(len(INPUT_NAME+INPUT_VALUE)/TERM_WIDTH)
                move_terminal_cursor(0, next_row)
                print(INPUT_NAME, end="", flush=True)     
                INPUT_ROW = next_row
                send_msg()
                INPUT_VALUE = ""

            elif key == b'\x08': #If backspace key       
                if move_cursor_left() == 1:
                    new_cursor_pos = get_terminal_cursor_position()
                    print(INPUT_VALUE[input_cursor_index:]+" ", end="", flush=True)
                    move_terminal_cursor(*new_cursor_pos)
                    INPUT_VALUE = INPUT_VALUE[:input_cursor_index-1] + INPUT_VALUE[input_cursor_index:]  

            elif key == b'\t': #If tab key
                print("\t", end="", flush=True)
                new_cursor_pos = get_terminal_cursor_position()
                print(INPUT_VALUE[input_cursor_index:], end="", flush=True)
                move_terminal_cursor(*new_cursor_pos)
                INPUT_VALUE = INPUT_VALUE[:input_cursor_index] + " "*8 + INPUT_VALUE[input_cursor_index:] 
        
            else: #If anything else
                char = key.decode('utf-8')
                print(char, end="", flush=True)
                new_cursor_pos = get_terminal_cursor_position()
                print(INPUT_VALUE[input_cursor_index:], end="", flush=True)
                move_terminal_cursor(*new_cursor_pos)
                INPUT_VALUE = INPUT_VALUE[:input_cursor_index] + char + INPUT_VALUE[input_cursor_index:]   

def init_input():
    global INPUT_NAME
    
    print(INPUT_NAME, end="", flush=True)

def init_server_socket():
    global SERVER_SOCKET
    global CLIENT_CONNECTION
    global CLIENT_ADDR
    global ADDR
    
    SERVER_SOCKET = socket.socket()
    SERVER_SOCKET.bind(ADDR)
    SERVER_SOCKET.listen(5)

    CLIENT_CONNECTION, CLIENT_ADDR = SERVER_SOCKET.accept()
    print(f"Accepted connection with {':'.join(map(str, CLIENT_ADDR))}...\n")
    
def stop_chat():
    global TERM_WIDTH
    global SERVER_SOCKET
    global CLIENT_CONNECTION
    
    CLIENT_CONNECTION.close()
    SERVER_SOCKET.close()
    enable_terminal_resize()
    print("\r"+" "*(TERM_WIDTH-1), end="", flush=True)
    exit()

def send_msg():
    global INPUT_VALUE
    global CLIENT_CONNECTION
    
    msg_bin = INPUT_VALUE.encode('utf-8')
    CLIENT_CONNECTION.send(msg_bin)
    
    if INPUT_VALUE in STOP_WORDS:
        stop_chat()

def recv_msg():
    global CLIENT_CONNECTION
    
    iobuffer = [CLIENT_CONNECTION]
    rlist, _, _ = select.select(iobuffer, [], [], 0)

    for socket in rlist:
        msg_bin = socket.recv(2048)
        msg_str = msg_bin.decode('utf-8')
        append_msg(f"Client Message: {msg_str}")
    
        if msg_str in STOP_WORDS:
            stop_chat()
    
#Resize terminal and prevent user from resizing it
#This is done to prevent errors with the input display due to character wrapping and etc.
TERM_WIDTH = 120
TERM_HEIGHT = 30

disable_terminal_resize()
set_terminal_size(TERM_WIDTH, TERM_HEIGHT)

STOP_WORDS = ["quit", "bye", "leave"]
HOST = '127.0.0.1'
PORT = 2000
ADDR = (HOST, PORT)  

init_server_socket()

INPUT_ROW = 2
INPUT_NAME = "Server Message: "
INPUT_VALUE = ""

init_input()

while True:
    handle_input()
    recv_msg()
