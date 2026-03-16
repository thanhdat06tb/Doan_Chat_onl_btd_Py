import json
import os
import random
import socket
import threading
import time
import tkinter as tk
from tkinter import simpledialog

import giao_dien as gd

DIA_CHI_MAY = "127.0.0.1"
CONG = 5555
IMG_DIR = "img"
BANG_MAU_AVATAR = ["#F9C74F", "#4CC9F0", "#B5179E", "#F94144", "#43AA8B"]
DINH_DANG_ANH = (".png", ".gif", ".jpg", ".jpeg")


class Khach_chat:
    def __init__(self):
        self.kenh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kenh.connect((DIA_CHI_MAY, CONG))

        self.cua_so = tk.Tk()
        gd.cau_hinh_cua_so(self.cua_so)

        self.biet_danh = simpledialog.askstring(
            "Tên", "Nhập tên của bạn:", parent=self.cua_so
        )
        if self.biet_danh:
            self.biet_danh = self.biet_danh.strip()
        if not self.biet_danh:
            self.biet_danh = "Anonymous"
        self._biet_danh_chuan = self.biet_danh.casefold()
        self.cua_so.title(f"Chat Online - {self.biet_danh}")

        self.avatar_color = random.choice(BANG_MAU_AVATAR)
        self.avatar_image = None
        self._anh_xem_truoc = []

        gd.tao_dau_trang(self)
        gd.tao_khung_chat(self)
        gd.tao_phan_nhap(self)

        self._gui_json({"type": "hello", "nickname": self.biet_danh})

        luong_nhan = threading.Thread(target=self.nhan, daemon=True)
        luong_nhan.start()

        self.cua_so.protocol("WM_DELETE_WINDOW", self.dung)
        self.cua_so.mainloop()

    def _cap_nhat_khung_tin(self, _event) -> None:
        self.khung_chat.configure(scrollregion=self.khung_chat.bbox("all"))
        self.khung_chat.yview_moveto(1.0)

    def _cap_nhat_canvas(self, event) -> None:
        self.khung_chat.itemconfigure(self._cua_so_tin_nhan, width=event.width)

    def _cuon_chuot(self, event) -> None:
        delta = int(-1 * (event.delta / 120))
        self.khung_chat.yview_scroll(delta, "units")

    def _gui_json(self, du_lieu: dict) -> None:
        payload = (json.dumps(du_lieu, ensure_ascii=False) + "\n").encode("utf-8")
        self.kenh.sendall(payload)

    def _dinh_dang_gio(self, ts) -> str:
        try:
            ts_f = float(ts)
        except Exception:
            ts_f = time.time()
        return time.strftime("%H:%M", time.localtime(ts_f))

    def _tai_anh_tu_file(self, duong_dan: str):
        try:
            try:
                from PIL import Image, ImageTk

                img_pil = Image.open(duong_dan)
                w, h = img_pil.size
                ty_le = max(w // 40, h // 40, 1)
                if ty_le > 1:
                    img_pil = img_pil.resize(
                        (w // ty_le, h // ty_le), Image.Resampling.LANCZOS
                    )
                return ImageTk.PhotoImage(img_pil)
            except ImportError:
                img = tk.PhotoImage(file=duong_dan)
                w, h = img.width(), img.height()
                ty_le = max(w // 40, h // 40, 1)
                if ty_le > 1:
                    img = img.subsample(ty_le, ty_le)
                return img
        except Exception:
            return None

    def doi_avatar(self):
        cua_so_chon = tk.Toplevel(self.cua_so)
        cua_so_chon.title("Chọn avatar")
        cua_so_chon.configure(bg=gd.MAU["nen_chinh"])
        cua_so_chon.geometry("360x280")

        tieu_de = tk.Label(
            cua_so_chon,
            text="Chọn ảnh trong thư mục img",
            bg=gd.MAU["nen_chinh"],
            fg=gd.MAU["chu_trang"],
            font=gd.FONT["trang_thai"],
        )
        tieu_de.pack(pady=(10, 6))

        khung_anh = tk.Frame(cua_so_chon, bg=gd.MAU["nen_chinh"])
        khung_anh.pack(fill="both", expand=True, padx=10, pady=6)

        files = []
        if os.path.isdir(IMG_DIR):
            for ten in os.listdir(IMG_DIR):
                duong_dan = os.path.join(IMG_DIR, ten)
                if os.path.isfile(duong_dan) and ten.lower().endswith(DINH_DANG_ANH):
                    files.append(duong_dan)

        self._anh_xem_truoc = []
        if not files:
            tk.Label(
                khung_anh,
                text="Thư mục img đang trống",
                bg=gd.MAU["nen_chinh"],
                fg=gd.MAU["chu_phu"],
            ).pack(pady=20)
        else:
            cot = 4
            for i, duong_dan in enumerate(files):
                anh = self._tai_anh_tu_file(duong_dan)
                if anh is None:
                    continue
                self._anh_xem_truoc.append(anh)
                nut = tk.Button(
                    khung_anh,
                    image=anh,
                    bd=0,
                    relief="flat",
                    bg=gd.MAU["nen_chinh"],
                    activebackground=gd.MAU["nen_chinh"],
                    command=lambda p=duong_dan: self._chon_avatar_tu_file(
                        p, cua_so_chon
                    ),
                )
                nut.grid(row=i // cot, column=i % cot, padx=6, pady=6)

        khung_duoi = tk.Frame(cua_so_chon, bg=gd.MAU["nen_chinh"])
        khung_duoi.pack(fill="x", pady=(0, 10))

        tk.Button(
            khung_duoi,
            text="Ngẫu nhiên màu",
            command=lambda: self._chon_mau_ngau_nhien(cua_so_chon),
            bg=gd.MAU["nen_nut_chinh"],
            fg=gd.MAU["chu_trang"],
            bd=0,
            relief="flat",
            padx=10,
            pady=6,
        ).pack(side="right", padx=10)

    def _chon_avatar_tu_file(self, duong_dan: str, cua_so_chon: tk.Toplevel) -> None:
        anh = self._tai_anh_tu_file(duong_dan)
        if anh is not None:
            self.avatar_image = anh
        gd.cap_nhat_avatar(self)
        cua_so_chon.destroy()

    def _chon_mau_ngau_nhien(self, cua_so_chon: tk.Toplevel) -> None:
        self.avatar_image = None
        self.avatar_color = random.choice(BANG_MAU_AVATAR)
        gd.cap_nhat_avatar(self)
        cua_so_chon.destroy()

    def _them_vao_khung(self, goi: dict) -> None:
        loai = goi.get("type")
        gio = self._dinh_dang_gio(goi.get("ts"))
        if loai == "chat":
            nguoi_gui = (goi.get("nickname") or "").strip()
            noi_dung = (goi.get("text") or "").strip()
            if not nguoi_gui or not noi_dung:
                return
            la_toi = nguoi_gui.casefold() == self._biet_danh_chuan
            gd.them_bong_tin(
                app=self,
                nguoi_gui=nguoi_gui,
                noi_dung=noi_dung,
                la_toi=la_toi,
                thoi_gian=gio,
            )
        elif loai == "system":
            noi_dung = (goi.get("text") or "").strip()
            if not noi_dung:
                return
            gd.them_bong_tin(
                app=self,
                nguoi_gui="Hệ thống",
                noi_dung=noi_dung,
                la_toi=False,
                thoi_gian=gio,
            )

    def _doc_dong(self):
        bo_dem = ""
        while True:
            du_lieu = self.kenh.recv(4096)
            if not du_lieu:
                break
            bo_dem += du_lieu.decode("utf-8", errors="replace")
            while "\n" in bo_dem:
                dong, bo_dem = bo_dem.split("\n", 1)
                dong = dong.strip()
                if dong:
                    yield dong
        if bo_dem.strip():
            yield bo_dem.strip()

    def nhan(self):
        try:
            for dong in self._doc_dong():
                try:
                    goi = json.loads(dong)
                except json.JSONDecodeError:
                    continue

                if goi.get("type") == "welcome":
                    for item in goi.get("history", []):
                        self.cua_so.after(0, self._them_vao_khung, item)
                    # Sau khi nạp xong lịch sử, đợi giao diện cập nhật rồi cuộn xuống cuối
                    self.cua_so.after(50, lambda: self.khung_chat.yview_moveto(1.0))
                else:
                    self.cua_so.after(0, self._them_vao_khung, goi)
        except Exception:
            pass

    def gui(self):
        text = self.nhap.get().strip()
        if not text:
            return
        try:
            self._gui_json({"type": "chat", "text": text, "ts": time.time()})
        except Exception:
            pass
        self.nhap.delete(0, "end")

    def dung(self):
        try:
            self.kenh.close()
        finally:
            self.cua_so.destroy()


def chay():
    Khach_chat()


if __name__ == "__main__":
    chay()
