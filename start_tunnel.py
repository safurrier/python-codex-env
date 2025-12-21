"""Start ngrok tunnel for the Flask app."""
from pyngrok import ngrok

# Create tunnel to Flask app on port 5000
public_url = ngrok.connect(5000)

print(f"\n🌐 Public URL: {public_url}\n")
print("Tunnel is active. Press Ctrl+C to stop.")

try:
    # Keep the script running
    ngrok.get_tunnels()
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down tunnel...")
    ngrok.kill()
