from tessa import Symbol

def test_vale3():
    try:
        print("Testando busca de informações do VALE3...")
        symbol = Symbol("VALE3")
        
        print("\nTestando busca de preço atual...")
        latest_price = symbol.price_latest()
        print(f"\nPreço atual: {latest_price}")
        
        print("\nTestando busca de histórico de preços...")
        history = symbol.price_history()
        print("\nÚltimos preços:")
        print(history.tail())
        
        return True
    except Exception as e:
        print(f"\nErro ao buscar dados: {str(e)}")
        return False

if __name__ == "__main__":
    test_vale3() 