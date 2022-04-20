<!-- :: Batch section
@echo off
setlocal

echo Select an option:
for /F "delims=" %%a in ('mshta.exe "%~F0"') do set "HTAreply=%%a"
echo End of HTA window, reply: "%HTAreply%"
goto :EOF
-->


<HTML>
<HEAD>
<HTA:APPLICATION SCROLL="no" SYSMENU="no" >

<TITLE>Drive</TITLE>
<SCRIPT language="JavaScript">
window.resizeTo(374,100);

function startApp(){
    Set WshShell = CreateObject("WScript.Shell");
    var dirPath = document.getElementById("dirName").value;
    /*var fso = new ActiveXObject("Scripting.FileSystemObject");
    fso.GetStandardStream(1).WriteLine(dirPath);*/
    WshShell.Run "cmd.exe /C python client.py 127.0.0.1 12345 dirPath 4";
    window.close();
}

</SCRIPT>
</HEAD>
<BODY>
    <label for="dirName">Diretory Name:</label>
    <input id="dirName" type="text"></input>
    <button onClick="startApp(2);"></button>

</BODY>
</HTML>