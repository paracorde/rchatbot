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
        if party_size > max(self.table_sizes.keys()): return None

        current = 0
        for size, n in self.table_sizes.items():
            if size < party_size:
                current += n
                continue

        return current
    
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
                for booking in self.available[table]: # also terribly inefficient if there are many bookings, could be improved by using a sorted dictionary
                    if booking < now: # booking already passed, delete to conserve storage
                        del self.available[table][booking]
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
                menu_item = self.menu[item]
                if 'allergens' in menu_item:
                    for allergen in menu_item['allergens']:
                        if allergen.lower() in [a.lower() for a in allergies]:
                            return {'error': f"Cannot place order. {menu_item['name']} contains {allergen} which you're allergic to."}
        
        # If no allergens found or no allergies provided, proceed with order
        for item in items:
            self.orders.append(item)
        return {
            'time': sum(self.menu[order]['time'] for order in self.orders),
            'cost': sum(self.menu[order]['price'] for order in self.orders)
        }
    
    def advance_queue(self):
        passed_time = int((time.time() - self.time)/60)
        while passed_time > 0:
            if (t := self.menu[self.orders[0]]['time']) > passed_time:
                passed_time -= t
                self.orders.pop(0)
            else:
                break
            
        self.time = time.time()
    
    def to_json(self):
        return json.dumps({'table_sizes': self.table_sizes, 'available': self.available, 'menu': self.menu, 'hours': self.hours, 'orders': self.orders, 'time': self.time})
    
    def from_json(json):
        r = Restaurant(json['table_sizes'], json['hours'], json['menu'], json['time'])
        r.orders = json['orders']
        r.available = json['available']
        r.advance_queue()
        return r
    
    def process_query(self, query):
        if query['operation'] == 'order':
            items = [[id]*count for id, count in query['items']]
            items = [j for i in items for j in i]
            allergies = query.get('allergies', None)
            return self.order(items, allergies)
        elif query['operation'] == 'get_available_times':
            t = Restaurant.to_restaurant_time(datetime.datetime.strptime(query['time'], '%d %b %Y, %H:%M').timestamp())
            times = self.get_available_times(query['party_size'], t)
            return [datetime.datetime.fromtimestamp(Restaurant.to_unix(i)).strftime('%d %b %Y, %H:%M') for i in times]
        elif query['operation'] == 'book':
            t = Restaurant.to_restaurant_time(datetime.datetime.strptime(query['time'], '%d %b %Y, %H:%M').timestamp())
            return self.book(query['party_size'], t)
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

