param([string]$file, [string]$fileData = "false")

If ($fileData -eq "false") {
	pscp -i "C:\Users\Jamie\Desktop\Pi Keys\PiPrivateKey.ppk" -scp "..\Gifs\Handled\$file" pi@192.168.0.50:"/home/pi/Desktop/Gifs/$file"
}
Else {
	pscp -i "C:\Users\Jamie\Desktop\Pi Keys\PiPrivateKey.ppk" -scp "..\Gifs\Database\$file" pi@192.168.0.50:"/home/pi/Desktop/Gifs/Database/$file"
}