'''
IMPORTS
'''
import eel
from screeninfo import get_monitors
from valclient.client import Client
import webbrowser
import os
import psutil

'''
CONSTANTS
'''

#Find the screen dimensions, reduce size x1.7 times. Scale window to that height.
SCREEN_DIMENSIONS = ( list(get_monitors())[0].width // 1.7, list(get_monitors())[0].height // 1.7 )

# Socials, don't touch! >:(
INSTAGRAM = 'https://www.instagram.com/kronsuki/'
GITHUB = 'https://github.com/SuppliedOrange/'

# Customize this to your preference
LOOP_DELAY = 4
LOCK_DELAY = 0
HOVER_DELAY = 0

# Used by the iterating runtime code
AGENT = None
SEEN_MATCHES = []
RUNNING = False

AGENT_CODES = { # All the codes right here so we don't need to fetch anything. This is also in web/json/agents.json so make changes in both places.
    "Jett": "add6443a-41bd-e414-f6ad-e58d267f4e95",
    "Reyna": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
    "Raze": "f94c3b30-42be-e959-889c-5aa313dba261",
    "Yoru": "7f94d92c-4234-0a36-9646-3a87eb8b5c89",
    "Phoenix": "eb93336a-449b-9c1b-0a54-a891f7921d69",
    "Neon": "bb2a4828-46eb-8cd1-e765-15848195d751",
    "Breach": "5f8d3a7f-467b-97f3-062c-13acf203c006",
    "Skye": "6f2a04ca-43e0-be17-7f36-b3908627744d",
    "Sova": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
    "Kayo": "601dbbe7-43ce-be57-2a40-4abd24953621",
    "Killjoy": "1e58de9c-4950-5125-93e9-a0aee9f98746",
    "Cypher": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
    "Sage": "569fdd95-4d10-43ab-ca70-79becc718b46",
    "Chamber": "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
    "Omen": "8e253930-4c05-31dd-1b6c-968525494517",
    "Brimstone": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
    "Astra": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
    "Viper": "707eab51-4836-f488-046a-cda6bf494859",
    "Fade": "dade69b4-4f5a-8528-247b-219e5a1facd6",
    "Harbor": "95b78ed7-4637-86d9-7e41-71ba8c293152",
    "Gekko": "e370fa57-4757-3604-3648-499e1f642d3f",
    "Deadlock": "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235"
}


'''
FUNCTIONS
'''
    
def get_region():
    '''
    Get the region code of the current game.
    '''
    with open(os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log'), 'rb') as f:
        lines = f.readlines()
    for line in lines:
        if b'regions' in line:
            region = line.split(b'regions/')[1].split(b']')[0]
            return region.decode()

def errorAlert( line1, line2, time ):
    '''
    Change the status text and the chosen agent text into an error.
    Sleep for some time before changing it back
    '''
    eel.alertUser(line1, line2)
    eel.sleep(time)
    eel.askUserToChooseAgent()

@eel.expose
def stop_lock():
    '''
    Change state from running to disabled to stop the locking process
    '''
    global RUNNING
    global AGENT
    RUNNING = False
    AGENT = None
    eel.hideStopButton()

@eel.expose
def try_lock( agent ):
    '''
    START TO ATTEMPT LOCKING AN AGENT
    '''
    global RUNNING
    global AGENT
    global SEEN_MATCHES

    # if valorant isnt on, mock the user
    if not "VALORANT.exe" in (p.name() for p in psutil.process_iter()):
        if RUNNING: stop_lock()
        return errorAlert("TURN VALORANT ON", "YOU CLOWN", 3)

    try: # try and get the region code automatically 
        region_code = get_region()
    except:
        if RUNNING: stop_lock()
        return errorAlert("COULD NOT FIND REGION", "TRY LOGGING IN AGAIN", 5)
    
    if RUNNING: # if we're already attempting to select an agent, simply change what agent we're trying to select
        # print(f'Agent changed to {agent} ') # DEBUG
        AGENT = AGENT_CODES[agent]
        return
    
    # print(f"Starting to lock {agent}") # DEBUG

    try:
        client = Client(region = region_code) # Activate 1 instance
    except ValueError:
        return errorAlert("COULD NOT FIND REGION", "TRY LOGGING IN AGAIN", 5)
    
    client.activate()
    # print("Activated 1 instance") # DEBUG

    RUNNING = True # Mark as actively trying to lock an agent

    while RUNNING:

        eel.sleep(LOOP_DELAY)

        if not RUNNING: return # Probably terminated

        # print("Rechecking...") # DEBUG

        try:

            sessionState = client.fetch_presence(client.puuid)['sessionLoopState']
            matchID = client.pregame_fetch_match()['ID']

            if (sessionState == "PREGAME" and matchID not in SEEN_MATCHES):

                SEEN_MATCHES.append(matchID) # If we've seen this match before, leave it be.
            
                eel.changeStatus("LOCKING")

                if not AGENT:
                    AGENT = AGENT_CODES[ agent ]

                eel.sleep(HOVER_DELAY)
                client.pregame_select_character(AGENT)

                eel.sleep(LOCK_DELAY)
                client.pregame_lock_character(AGENT)

                stop_lock()

                eel.changeStatus("LOCKED")

                return True

        except Exception as e:

            if "pre-game" not in str(e):
                errorAlert( "ERROR", e, 12 )
                stop_lock()
                return


@eel.expose
def open_instagram():
    webbrowser.open('https://www.instagram.com/kronsuki/')

@eel.expose
def open_github():
    webbrowser.open('https://github.com/SuppliedOrange/') 
    
'''
INITIALIZING THE EEL APPLICATION
'''
eel.init('web')
eel.start( 'index.html', size=(SCREEN_DIMENSIONS), port=0 )
