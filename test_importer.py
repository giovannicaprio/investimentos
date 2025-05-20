from app.importers.posicao_atual_importer import PosicaoAtualImporter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_importer():
    try:
        # Create importer instance
        importer = PosicaoAtualImporter("/tmp/posicaoAtual.csv")
        
        # Import data
        investments = importer.import_data()
        
        # Print results
        logger.info(f"Successfully imported {len(investments)} investments")
        
        # Print details of first investment for verification
        if investments:
            first_inv = investments[0]
            logger.info("\nFirst investment details:")
            logger.info(f"Name: {first_inv.name}")
            logger.info(f"Type: {first_inv.type}")
            logger.info(f"Current Share Value: {first_inv.current_share_value}")
            logger.info(f"Expected Return: {first_inv.expected_return}")
            if first_inv.purchases:
                purchase = first_inv.purchases[0]
                logger.info(f"Purchase Quantity: {purchase.quantity}")
                logger.info(f"Purchase Price: {purchase.price_per_share}")
                logger.info(f"Purchase Total: {purchase.total_value}")
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")

if __name__ == "__main__":
    test_importer() 