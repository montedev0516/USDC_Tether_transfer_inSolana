from solana.rpc.api import Client  
from solana.transaction import Transaction   
from solana.publickey import PublicKey  
from solana.keypair import Keypair  
from spl.token.instructions import transfer_checked, create_associated_token_account  
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID  
from spl.token.client import Token  

def transfer_usdc(sender_private_key: str, receiver_address: str, amount: float, endpoint="https://api.mainnet-beta.solana.com"):  
    """  
    Transfer USDC tokens between Solana wallets  
    
    :param sender_private_key: Sender's private key (base58 string)  
    :param receiver_address: Receiver's public key (base58 string)  
    :param amount: USDC amount to send (e.g., 1.5)  
    :param endpoint: Solana RPC endpoint  
    :return: Transaction signature  
    """  
    # USDC mint address  
    USDC_MINT = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  
    
    # Initialize connection  
    connection = Client(endpoint)  
    
    # Load sender keypair  
    sender_keypair = Keypair.from_base58_string(sender_private_key)  
    
    # Initialize token client  
    token_client = Token(  
        conn=connection,  
        pubkey=USDC_MINT,  
        program_id=TOKEN_PROGRAM_ID,  
        payer=sender_keypair  
    )  
    
    # Get token accounts  
    sender_token_account = token_client.get_associated_token_address(sender_keypair.public_key)  
    receiver_pubkey = PublicKey(receiver_address)  
    receiver_token_account = token_client.get_associated_token_address(receiver_pubkey)  
    
    # Create receiver token account if needed  
    receiver_account_info = connection.get_account_info(receiver_token_account)  
    if not receiver_account_info['result']['value']:  
        create_ix = create_associated_token_account(  
            payer=sender_keypair.public_key,  
            owner=receiver_pubkey,  
            mint=USDC_MINT  
        )  
        transaction = Transaction().add(create_ix)  
        connection.send_transaction(transaction, sender_keypair)  
    
    # Build transfer instruction  
    transfer_ix = transfer_checked(  
        program_id=TOKEN_PROGRAM_ID,  
        source=sender_token_account,  
        mint=USDC_MINT,  
        dest=receiver_token_account,  
        owner=sender_keypair.public_key,  
        amount=int(amount * 10**6),  # USDC has 6 decimals  
        decimals=6  
    )  
    
    # Create and send transaction  
    recent_blockhash = connection.get_latest_blockhash()['result']['value']['blockhash']  
    transaction = Transaction(  
        recent_blockhash=recent_blockhash,  
        fee_payer=sender_keypair.public_key  
    ).add(transfer_ix)  
    
    result = connection.send_transaction(transaction, sender_keypair)  
    return result['result']  

# Example usage  
if __name__ == "__main__":  
    # Sender private key (base58 format)  
    SENDER_PRIVATE_KEY = "...FdF8UJYM39qT8yPzrPtu8V4V5rBqaJEcSePq9m1H9N..."  
    
    # Receiver public key  
    RECEIVER_ADDRESS = "Eu2YNNdqW6MXEeL2Sfc8Qcw2VAreHy1wajgMsi15EU5a"  
    
    # Transfer parameters  
    AMOUNT_USDC = 1.0  # Amount to send  
    RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"  # Use devnet for testing  
    
    try:  
        tx_signature = transfer_usdc(SENDER_PRIVATE_KEY, RECEIVER_ADDRESS, AMOUNT_USDC, RPC_ENDPOINT)  
        print(f"Transaction successful! Signature: {tx_signature}")  
    except Exception as e:  
        print(f"Error: {str(e)}")