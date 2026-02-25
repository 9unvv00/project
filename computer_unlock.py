import tkinter as tk
import os
import time
import threading
import random
import json
from datetime import datetime
import wmi

# ==========================================
KEY_FILE_NAME = "unlock.key" 
CONFIG_FILE = "security_config.json" 
ADMIN_PASSWORD = "1234"
# ==========================================

def write_log(event_type, result):
    log_file = "log.json"
    log_entry = {
        "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "이벤트 종류": event_type,
        "결과": result
    }
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except:
            logs = []
    logs.append(log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

class MatrixRain(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg='black', highlightthickness=0)
        master.update()
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()
        self.pack(fill=tk.BOTH, expand=True)
        self.font_size = 14
        self.font = ("Courier", self.font_size, "bold")
        self.chars = [str(i) for i in range(10)] 
        self.cols = self.width // self.font_size
        self.drops = []
        for i in range(self.cols):
            x = i * self.font_size
            y = random.randint(-self.height, 0)
            text_content = "\n".join([random.choice(self.chars) for _ in range(random.randint(5, 15))])
            item_id = self.create_text(x, y, text=text_content, font=self.font, fill="#0F0", anchor="nw")
            self.drops.append({'id': item_id, 'speed': random.randint(3, 10)})
        self.running = True
        self.animate()

    def animate(self):
        if not self.running: return
        try:
            for drop in self.drops:
                self.move(drop['id'], 0, drop['speed'])
                coords = self.coords(drop['id'])
                if coords and coords[1] > self.height:
                    self.move(drop['id'], 0, random.randint(-500, -100) - coords[1])
                    new_text = "\n".join([random.choice(self.chars) for _ in range(random.randint(5, 15))])
                    self.itemconfigure(drop['id'], text=new_text)
        except: pass
        self.after(30, self.animate)

    def stop(self): self.running = False
    def start(self):
        if not self.running:
            self.running = True
            self.animate()

class USBKeyLockApp:
#메인 보안 클래스임
    def __init__(self, root):
        # Tkinter 메인 창 설정 및 단축키 차단, 설정파일로드, 백그라운드 USB 탐지시작
        self.root = root
        self.is_locked = True
        self.is_prompting_password = False 
        self.prev_usb_connected = False
        self.wmi_client = wmi.WMI()
        
        # JSON 설정 파일에서 시리얼과 토큰 부름
        self.expected_serial, self.expected_token = self.load_config()

        self.root.protocol("WM_DELETE_WINDOW", self.block_close)
        self.root.bind("<Alt-F4>", self.block_alt_f4)
        self.root.bind("<Control-Shift-KeyPress-Q>", self.emergency_exit)
        self.root.attributes('-fullscreen', True) 
        self.root.attributes('-topmost', True)    
        self.root.overrideredirect(True)          
        self.root.configure(bg='black')
        
        self.matrix_bg = MatrixRain(root)
        
        self.msg_frame = tk.Frame(root, bg='black')
        self.msg_frame.place(relx=0.5, rely=0.4, anchor='center')

        self.label = tk.Label(self.msg_frame, text="시스템 잠김\n\n발급된 USB 키를 연결하세요.", 
                              font=("맑은 고딕", 30, "bold"), fg="red", bg="black")
        self.label.pack(pady=20, padx=20)
        
        self.exit_btn = tk.Button(root, text="관리자 종료 (키 회수)", command=self.show_password_frame,
                                  font=("맑은 고딕", 12), bg="gray", fg="white", relief='flat')
        self.exit_btn.place(relx=0.5, rely=0.8, anchor='center')
        
        self.pass_frame = tk.Frame(root, bg="black", bd=2, relief="groove")
        
        self.setup_floating_widget()

        self.monitor_thread = threading.Thread(target=self.check_usb_loop, daemon=True)
        self.monitor_thread.start()

    def setup_floating_widget(self):
        #잠금이 해제되면 우측 하단에 작고 항상 떠 있는 제어창 생성함
        self.float_win = tk.Toplevel(self.root)
        self.float_win.overrideredirect(True)
        self.float_win.attributes('-topmost', True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 170
        y = screen_height - 150
        self.float_win.geometry(f"150x40+{x}+{y}")
        self.float_win.configure(bg='black')
        
        self.float_btn = tk.Button(self.float_win, text="🔒 보안 종료 (키 회수)", 
                                   command=self.show_password_frame,
                                   font=("맑은 고딕", 10, "bold"), bg="#8B0000", fg="white", relief='flat')
        self.float_btn.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        
        self.float_win.withdraw()

    def load_config(self):
        #pc에 저장된 설정파일을 읽어와서 허용된 USB 시리얼번호와 토큰 값을 반환
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("serial_number", ""), data.get("token", "")
            except Exception as e:
                write_log("오류", f"설정 파일 로드 실패: {e}")
        return "", ""

    def block_close(self): 
        #X버튼 눌러서 프로그램 종료하는 것을 막음
        return

    def block_alt_f4(self, event): 
        #alt + F4 단축키 입력 차단
        return "break"

    def emergency_exit(self, event=None):
        #비상 단축키임 로그에 남음
        write_log("비상 탈출", "숨겨진 단축키(Ctrl+Shift+Q)가 사용됨")
        self.matrix_bg.stop()
        self.root.destroy()

    def show_password_frame(self):
        #관리자 종료를 누르면 비밀번호 입력할 수 있는 UI
        self.is_prompting_password = True 
        self.float_win.withdraw() 
        
        self.root.deiconify()
        self.root.attributes('-topmost', True) 
        
        if self.pass_frame.winfo_ismapped(): return
        self.msg_frame.place_forget()
        self.exit_btn.place_forget()
        self.pass_frame.place(relx=0.5, rely=0.5, anchor="center")
        for widget in self.pass_frame.winfo_children(): widget.destroy()
        
        tk.Label(self.pass_frame, text="종료 시 키가 회수됩니다\n관리자 비밀번호 입력", font=("맑은 고딕", 12), bg="black", fg="white").pack(pady=5)
        self.pass_entry = tk.Entry(self.pass_frame, show="*", font=("맑은 고딕", 12), bg="#333", fg="white", insertbackground='white')
        self.pass_entry.pack(pady=5, padx=10)
        self.pass_entry.focus_set()
        self.pass_entry.bind("<Return>", self.check_password)

        btn_box = tk.Frame(self.pass_frame, bg="black")
        btn_box.pack(pady=10)
        tk.Button(btn_box, text="확인", command=self.check_password, width=8, bg='gray', fg='white', relief='flat').pack(side="left", padx=5)
        tk.Button(btn_box, text="취소", command=self.hide_password_frame, width=8, bg='gray', fg='white', relief='flat').pack(side="left", padx=5)

    def hide_password_frame(self):
        #비밀번호 입력 UI를 숨기고 잠금 화면 상태로 돌아감
        self.pass_frame.place_forget()
        self.msg_frame.place(relx=0.5, rely=0.4, anchor='center')
        self.exit_btn.place(relx=0.5, rely=0.8, anchor='center')
        self.is_prompting_password = False 

    def revoke_key_and_exit(self):
        try:
            #관리자 인증 성공 시, 키 파일 삭제 및 프로그램 종료
            usb_disks = self.wmi_client.Win32_LogicalDisk(DriveType=2)
            for disk in usb_disks:
                if disk.VolumeSerialNumber == self.expected_serial:
                    key_path = os.path.join(disk.DeviceID + "\\", KEY_FILE_NAME)
                    if os.path.exists(key_path):
                        os.remove(key_path) 
                        write_log("키 회수", "USB에서 키 파일 정상 회수됨")
                    break
            
            # 종료 시 로컬 설정 파일도 삭제하여 초기화
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                
        except Exception as e:
            write_log("키 회수", f"회수 실패: {e}")

        self.matrix_bg.stop()
        self.root.destroy()

    def check_password(self, event=None):
        #관리자 비밀번호가 맞는지 확인
        if self.pass_entry.get() == ADMIN_PASSWORD:
            write_log("시스템 종료", "관리자 종료 승인")
            self.revoke_key_and_exit()
        else:
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.config(bg="red")
            self.root.after(200, lambda: self.pass_entry.config(bg="#333"))

    def lock_screen(self):
        #화면을 전체화면으로 덮어서 잠금시킴
        if not self.is_locked:
            self.float_win.withdraw() 
            self.root.deiconify()
            self.root.attributes('-topmost', True)
            
            self.is_locked = True
            self.pass_frame.place_forget()
            self.msg_frame.place(relx=0.5, rely=0.4, anchor='center')
            self.exit_btn.place(relx=0.5, rely=0.8, anchor='center')
            self.matrix_bg.start()

    def unlock_screen(self):
        #USB가 꽂혀있을 때 잠금화면을 숨기고 setup_floating_widget 함수 실행
        if self.is_locked:
            self.matrix_bg.stop()
            self.root.withdraw()
            self.float_win.deiconify() 
            self.is_locked = False

    def check_usb_loop(self):
        #1초마다 USB 드라이브 스캔함
        import pythoncom
        pythoncom.CoInitialize()
        thread_wmi = wmi.WMI()

        while True:
            if self.is_prompting_password:
                time.sleep(1)
                continue

            correct_usb_found = False
            usb_connected = False
            
            if not self.expected_token or not self.expected_serial:
                self.root.after(0, self.lock_screen)
                self.root.after(0, lambda: self.label.config(text="키 미발급\n\nsetting.py를 통해 키를 발급받으세요."))
                time.sleep(1)
                continue

            try:
                usb_disks = thread_wmi.Win32_LogicalDisk(DriveType=2)
                for disk in usb_disks:
                    usb_connected = True
                    current_serial = disk.VolumeSerialNumber 
                    
                    # 동적으로 저장된 시리얼 번호와 비교
                    if current_serial == self.expected_serial:
                        key_path = os.path.join(disk.DeviceID + "\\", KEY_FILE_NAME)
                        if os.path.exists(key_path):
                            with open(key_path, "r", encoding="utf-8") as f:
                                file_content = f.read().strip()
                                
                            if file_content == self.expected_token:
                                correct_usb_found = True
                                break 
            except Exception:
                pass

            if correct_usb_found:
                self.root.after(0, self.unlock_screen)
            else:
                self.root.after(0, self.lock_screen)
                if usb_connected:
                    self.root.after(0, lambda: self.label.config(text="USB/키 불일치\n\n지급된 키가 아니거나 등록되지 않은 기기입니다."))
                else:
                    self.root.after(0, lambda: self.label.config(text="시스템 잠김\n\n발급된 USB 키를 연결하세요."))

            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = USBKeyLockApp(root)
    root.mainloop()