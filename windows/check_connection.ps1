param(
    [string]$ServerIP = '192.168.232.131',
    [string]$LabUser = 'lab'
)
Test-NetConnection $ServerIP -Port 22
ssh "$LabUser@$ServerIP"
