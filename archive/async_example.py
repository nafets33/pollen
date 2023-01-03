def async_api_alpaca__queenOrders(queen_order__s): # re-initiate for i timeframe 

    async def get_changelog(session, order_id, queen_order):
        async with session:
            try:
                order_status = check_order_status(api=api, client_order_id=order_id, queen_order=queen_order)
                return {'client_order_id': order_id, 'order_status': order_status}
            except Exception as e:
                print(e, order_id)
                logging.error((str(order_id), str(e)))
                raise e
    
    async def main(queen_order__s):

        async with aiohttp.ClientSession() as session:
            return_list = []
            tasks = []
            for order_id, queen_order in queen_order__s.items(): # castle: [spy], bishop: [goog], knight: [META] ..... pawn1: [xmy, skx], pawn2: [....]
                # print(qcp)
                tasks.append(asyncio.ensure_future(get_changelog(session, order_id, queen_order)))
            original_pokemon = await asyncio.gather(*tasks)
            for pokemon in original_pokemon:
                return_list.append(pokemon)
            
            return return_list

    x = asyncio.run(main(queen_order__s))
    # ipdb.set_trace()
    return True