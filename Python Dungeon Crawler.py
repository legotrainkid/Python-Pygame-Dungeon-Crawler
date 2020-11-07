import MENU
import logging

if __name__ == "__main__":
    logging.basicConfig(filename="error.log",
                        filemode="a",
                        format='\n\nVersion: 1.0.0'
                        + ' - %(name)s - %(levelname)s - %(message)s')
    try:
        menu = MENU.main()
    except:
        logging.exception(" An exception occured")
        print("error")
