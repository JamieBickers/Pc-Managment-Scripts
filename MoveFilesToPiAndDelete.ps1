$all_files = Get-Childitem "C:\\Users\\Jamie\\Desktop\\Gifs\\Handled"
Foreach ($file in $all_files) {
	try {
		pscp -i "C:\Users\Jamie\Desktop\Pi Keys\PiPrivateKey.ppk" -scp "..\Gifs\Handled\$file" pi@192.168.0.50:"/home/pi/Desktop/Gifs/$file"
		Remove-Item "..\Gifs\Handled\$file"
	}
	catch {
		continue
	}
}

pscp -i "C:\Users\Jamie\Desktop\Pi Keys\PiPrivateKey.ppk" -scp "..\Gifs\Database\FileData.xml" pi@192.168.0.50:"/home/pi/Desktop/Gifs/Database/FileData.xml"