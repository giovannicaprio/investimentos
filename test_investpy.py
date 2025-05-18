import investpy
import pandas as pd

def test_petr3():
    try:
        print("Testando busca de informações do PETR3...")
        stock_info = investpy.get_stock_information('PETR3', country='brazil')
        print("\nInformações encontradas:")
        print(stock_info)
        
        print("\nTestando busca de preços recentes...")
        recent_data = investpy.get_stock_recent_data('PETR3', country='brazil')
        print("\nÚltimos preços:")
        print(recent_data.tail())
        
        return True
    except Exception as e:
        print(f"\nErro ao buscar dados: {str(e)}")
        return False

if __name__ == "__main__":
    test_petr3() 