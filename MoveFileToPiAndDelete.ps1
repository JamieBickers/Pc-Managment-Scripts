param([string]$file)
pscp -i "C:\Users\Jamie\Desktop\Pi Keys\PiPrivateKey.ppk" -scp "..\Gifs\Handled\$file" pi@192.168.0.50:"/home/pi/Desktop/Gifs/$file"