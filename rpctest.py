from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

def message(service_name, parameters):
    print "Service: " + service_name + " Parmameters: " + parameters

if __name__ == "__main__":
    print "Starting..."
    server = SimpleJSONRPCServer(addr=(("0.0.0.0", 8801)), logRequests=True)
    server.register_function(message, "message")
    server.serve_forever()
    
