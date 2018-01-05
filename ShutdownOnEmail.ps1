try {
	[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing") 
	[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") 

	$webclient = new-object System.Net.WebClient
	$webclient.Credentials = new-object System.Net.NetworkCredential ("jamiebickerspcmanager@googlemail.com", "yM05YkJWGirq")

	function handleEmailSubject {
		Param([String]$subject)
		$subject = $subject.ToLower() -replace '\s', ''
		if ($subject -eq "shutdown") {
			& "C:\Windows\System32\shutdown.exe" /s
			Exit
		}
		elseif (($subject -eq "hibernate") -Or ($subject -eq "sleep")) {
			[System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)
			Exit
		}
	}
	For ($i = 0; $i -lt 5; $i++) {
		[xml]$xml= $webclient.DownloadString("https://mail.google.com/mail/feed/atom")
		$emails = $xml.feed.entry
		$now = [System.DateTime]::Now

		$os = Get-WmiObject -Class win32_operatingsystem
		$startupTime = $os.ConvertToDateTime($os.LastBootUpTime)

		foreach ($email in $emails) {
			$timeEmailWasSent = [datetime]$email.issued
			if ([int](($now-$timeEmailWasSent).totalminutes) -lt 3) {
				if ([int](($startupTime-$timeEmailWasSent).totalseconds) -lt 0) {
					handleEmailSubject($email.title)
				}
			}
		}
		Start-Sleep -s 60
	}
}
catch {
	Exit
}