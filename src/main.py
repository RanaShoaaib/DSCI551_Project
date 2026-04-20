from db import get_connection
from setup_db import initialize_database
from actions import get_sample_user_name, get_sample_user_id, browse_recent_items, retrieve_items_by_category, retrieve_items_by_status, get_items_by_user_id, get_items_by_user_name
from utils import get_menu_option, get_mode_option, print_results
from mvcc import demo_mvcc

def main():
    conn = get_connection()
    try :
        initialize_database(conn, False)

        while True:
            option = get_menu_option()
            if option == 7:
                break

            if option in range(1, 6):
                mode = get_mode_option()

            match option:
                case 1:
                    header,results = browse_recent_items(conn,'traffic',20, mode)
                    print()
                    print_results(mode, header,results)
                case 2:
                    header,results = retrieve_items_by_category(conn,'crime', mode)
                    print()
                    print_results(mode, header,results)
                case 3:
                    header,results = retrieve_items_by_status(conn,'open', mode)
                    print()
                    print_results(mode, header,results)
                case 4:
                    user_id = get_sample_user_id(conn)
                    print(f"\nUsing user id: {user_id}")
                    header,results = get_items_by_user_id(conn,user_id, mode)
                    print_results(mode, header,results)
                case 5:
                    user_name = get_sample_user_name(conn)
                    print(f"\nUsing user name: {user_name}")
                    header, results = get_items_by_user_name(conn, user_name, mode)
                    print_results(mode, header,results)
                case 6:
                    demo_mvcc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()