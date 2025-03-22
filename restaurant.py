import time
import datetime
import json

overlap = lambda x, y: x[0] <= y[1] and y[0] <= x[1]

class Restaurant:
    def to_restaurant_time(timestamp):
        return int(timestamp) // (60 * 15)
    
    def to_unix(timestamp):
        return int(timestamp) * (60 * 15)

    def __init__(self, table_sizes, hours, menu, t=None):
        self.table_sizes = {size: table_sizes[size] for size in sorted(table_sizes.keys())}
        self.tables = sum(self.table_sizes.values())
        self.available = {i: {} for i in range(self.tables)}
        self.menu = menu
        self.hours = hours
        self.orders = []
        self.time = t or time.time()
    
    def get_viable_tables(self, party_size):
        # Convert party_size to integer if it's a string
        if isinstance(party_size, str):
            party_size = int(party_size)
        
        # Convert table_sizes keys to integers for comparison
        max_size = max(int(size) for size in self.table_sizes.keys())
        if party_size > max_size:
            return None

        current = 0
        for size, n in self.table_sizes.items():
            size_int = int(size) if isinstance(size, str) else size
            if size_int < party_size:
                current += n
                continue
            
            # Found a table size that can accommodate the party
            return current

        # If we've gone through all sizes and none are suitable
        return None
    
    def get_available_times(self, party_size, start, length=4, surrounding=4):
        dt = datetime.datetime.fromtimestamp(Restaurant.to_unix(start))
        week_beginning = Restaurant.to_restaurant_time((dt - datetime.timedelta(days=dt.weekday(), hours=dt.hour)).timestamp())
        now = Restaurant.to_restaurant_time(datetime.datetime.now().timestamp())

        viable = self.get_viable_tables(party_size)
        if viable is None: # no viable tables, party size is too large
            return []
        
        available = []
        for offset in range(-surrounding, surrounding+1):
            s = start + offset
            e = s + length

            if s < now:
                continue

            obeys_hours = False
            for open, close in self.hours:
                if s-week_beginning >= open and e-week_beginning <= close: # entirely contained within opening hours 
                    obeys_hours = True
                    break
            if not obeys_hours:
                continue

            # this is pretty terribly inefficient, but it's a very limited number of operations so it's okay
            for table in range(viable, self.tables):
                if table not in self.available:  # Skip if table index is invalid
                    continue
                
                # Process bookings for this table
                bookings_to_remove = []
                for booking in self.available[table]:
                    if booking < now: # booking already passed, delete to conserve storage
                        bookings_to_remove.append(booking)
                
                # Remove expired bookings
                for booking in bookings_to_remove:
                    del self.available[table][booking]
                
                # Check if all required time slots are available
                for t in range(s, e):
                    if not self.available[table].get(t, True): # table is not available
                        break
                else:
                    available.append(s) # at least one table can be booked during this time
                    break # so we no longer need to check any other tables
        
        return available

    def book(self, party_size, start, length=4): # returns True on success
        viable = self.get_viable_tables(party_size)
        if viable is None:
            return False
        
        s = start
        e = s + length
        for table in range(viable, self.tables):
            # Skip if table doesn't exist in available dictionary
            if table not in self.available:
                continue
            
            for t in range(s, e):
                if not self.available[table].get(t, True):
                    break
            else:
                for t in range(s, e):
                    self.available[table][t] = False
                return table

        return False

    def order(self, items, allergies=None):
        # Check for allergens if allergies are provided
        if allergies:
            for item in items:

                item_key = int(item) if isinstance(item, str) else item

                menu_item = self.menu[item_key]
                if 'allergens' in menu_item:
                    for allergen in menu_item['allergens']:
                        if allergen.lower() in [a.lower() for a in allergies]:
                            return {'error': f"Cannot place order. {menu_item['name']} contains {allergen} which you're allergic to."}
        
        # If no allergens found or no allergies provided, proceed with order
        valid_items = []
        for item in items:
            item_key = int(item) if isinstance(item, str) else item
            if item_key in self.menu:
                valid_items.append(item_key)
            else:
                return {'error': f"Item {item_key} not found in the menu."}
        
        # Add valid items to orders
        for item in valid_items:
            self.orders.append(item)
        
        # Calculate time and cost based on valid items
        return {
            'time': sum(self.menu[item]['time'] for item in self.orders),
            'cost': sum(self.menu[item]['price'] for item in self.orders)
        }
    
    def advance_queue(self):
        passed_time = int((time.time() - self.time)/60)
        while passed_time > 0:
            if self.orders and ((t := self.menu[self.orders[0]]['time']) > passed_time): #fix by Clinton. Only execute when order list is not empty
                passed_time -= t
                self.orders.pop(0)
            else:
                break
            
        self.time = time.time()
    
    def to_json(self):
        return json.dumps({'table_sizes': self.table_sizes, 'available': self.available, 'menu': self.menu, 'hours': self.hours, 'orders': self.orders, 'time': self.time})
    
    def from_json(inputJson):
        loadedJson = json.loads(inputJson)
        
        # Convert menu keys from strings to integers before creating the Restaurant instance
        if 'menu' in loadedJson and isinstance(loadedJson['menu'], dict):
            menu_with_int_keys = {}
            for key, value in loadedJson['menu'].items():
                menu_with_int_keys[int(key)] = value
            loadedJson['menu'] = menu_with_int_keys
        
        r = Restaurant(loadedJson['table_sizes'], loadedJson['hours'], loadedJson['menu'], loadedJson['time'])
        r.orders = loadedJson['orders']
        
        # Convert string keys back to integers for the available dictionary
        r.available = {}
        for key, value in loadedJson['available'].items():
            # Convert the outer key (table number) to int
            r.available[int(key)] = {}
            for booking_time, booking_status in value.items():
                # Convert the inner keys (booking times) to int
                r.available[int(key)][int(booking_time)] = booking_status
        
        r.advance_queue()
        return r
    
    def process_query(self, query):
        if query['operation'] == 'order':
            # Validate items before processing
            for item_id, count in query['items']:
                # Convert to int if it's a string
                item_id = int(item_id) if isinstance(item_id, str) else item_id
                if item_id not in self.menu:
                    return {'error': f"Item {item_id} not found in the menu."}
            
            # Process valid items
            items = [[id]*count for id, count in query['items']]
            items = [j for i in items for j in i]
            allergies = query.get('allergies', None)
            return self.order(items, allergies)
        elif query['operation'] == 'get_available_times':
            t = Restaurant.to_restaurant_time(datetime.datetime.strptime(query['time'], '%d %b %Y, %H:%M').timestamp())
            # Convert party_size to int
            party_size = int(query['party_size']) if isinstance(query['party_size'], str) else query['party_size']
            times = self.get_available_times(party_size, t)
            return [datetime.datetime.fromtimestamp(Restaurant.to_unix(i)).strftime('%d %b %Y, %H:%M') for i in times]
        elif query['operation'] == 'book':
            t = Restaurant.to_restaurant_time(datetime.datetime.strptime(query['time'], '%d %b %Y, %H:%M').timestamp())
            # Convert party_size to int
            party_size = int(query['party_size']) if isinstance(query['party_size'], str) else query['party_size']
            return self.book(party_size, t)
        elif query['operation'] == 'recommend':
            # Return menu items for the LLM to generate recommendations
            preferences = query.get('preferences', [])
            context = query.get('context', '')
            allergies = query.get('allergies', [])
            return {
                'menu_items': {id: item for id, item in self.menu.items()},
                'preferences': preferences,
                'context': context,
                'allergies': allergies
            }
    # self.reservations = {[] for _ in sum(table_sizes.values())}
    # def get_available_table(self, party_size, start, length):
    #     end = start + length
    #     current = 0
    #     for size, n in self.table_sizes.items():
    #         if size < party_size:
    #             current += n
    #             continue
    #         for _ in range(n):
    #             result = self.query_table_availability(self, current, start, end)
    #             if result:
    #                 return current
    #             current += 1
    #     return None

    # def query_table_availability(self, table, start, end):
    #     index = bisect.bisect_right(self.reservations[table], (start, end))
    #     if index > 0:

# dt = datetime.datetime.now()
# t = Restaurant.to_restaurant_time(dt.timestamp()) + 4
# print(twenty_eight.get_available_times(4, t))
# print(t, twenty_eight.available)
# print(twenty_eight.book(4, t))
# print(twenty_eight.available)
# print(twenty_eight.book(6, t))
# print(twenty_eight.available)
# print(twenty_eight.get_available_times(4, t))

