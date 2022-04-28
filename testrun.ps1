&$PSScriptRoot\flaskEnv\Scripts\Activate.ps1
$env:FLASK_ENV = "development"
Invoke-Expression "flask run"