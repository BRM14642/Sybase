import uno

def test_uno():
    try:
        local_context = uno.getComponentContext()
        print("uno module is configured correctly.")
    except Exception as e:
        print(f"Error: {e}")

test_uno()