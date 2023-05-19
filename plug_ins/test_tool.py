import win32clipboard
import win32con as wc
win32clipboard.OpenClipboard()
text = "fafg"
win32clipboard.SetClipboardData(wc.CF_TEXT,text.encode("gbk"))
win32clipboard.CloseClipboard()