' Crea un objeto Shell para ejecutar comandos
Set WshShell = CreateObject("WScript.Shell")

' Obtiene la ruta del directorio donde se encuentra este script VBS
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Construye la ruta completa al archivo batch
batPath = fso.BuildPath(scriptDir, "start_server.bat")

' Ejecuta el archivo batch en una ventana oculta (0) y no espera a que termine (False)
WshShell.Run """" & batPath & """", 0, False
