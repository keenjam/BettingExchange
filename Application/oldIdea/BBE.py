import subprocess

def initialiseExchange():
    '''
    Initialise betting exchange
    '''
    exchangeProcess = subprocess.Popen("./Server/exchange.out", shell=True)
    return exchangeProcess

def initialiseAgent(agent):
    '''
    Initialise betting agent
    '''
    url = "./Clients/" + agent
    agentProcess = subprocess.Popen(url, shell=False)
    return agentProcess

def destroyProcess(process):
    '''
    Destroy instance of process
    '''
    process.kill()
    process.terminate()

if __name__ == "__main__":
    # initialise program
    exchangeProcess1 = initialiseExchange()
    agentProcess1 = initialiseAgent("Test_Betting_Agent.py")
    agentProcess2 = initialiseAgent("Test_Betting_Agent2.py")
    while(True):
        i = 1
    #destroyProcess(agentProcess1)
    #destroyProcess(exchangeProcess1)
