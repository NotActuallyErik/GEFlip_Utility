import requests, time, webbrowser, os


class GEPrices:
    f_volume:   int     = 0
    f_high:     int     = 0
    f_low:      int     = 0
    f_margin:   int     = 0
    f_roi:      float   = 0.0

    scan_mode:  str     = "High Margin"
    w_filter:   list    = ['(unf)', '(1)', '(2)', '(3)', '(4)', 'grimy']

    data_cache: dict    = {}
    saved:      dict    = {}

    def __init__(self):
        self.set_mode('2')

    def get_volumes(self):
        r = requests.get("https://prices.runescape.wiki/api/v1/osrs/volumes")
        return self.filter_volumes(r.json())

    def get_mappings(self):
        r = requests.get("https://prices.runescape.wiki/api/v1/osrs/mapping")
        return r.json()

    def get_prices(self):
        r = requests.get("https://prices.runescape.wiki/api/v1/osrs/latest")
        return r.json()

    def filter_volumes(self, volumes):
        filtered_data = {}
        for i in volumes['data']:
            if volumes['data'][i] > self.f_volume:
                filtered_data[i] = volumes['data'][i]
        return filtered_data

    def map_volumes(self, volumes, mapping):
        mapped = {}
        for i in mapping:
            if not str(i['id']) in volumes:
                continue
            try:
                mapped[i['id']] = {
                    'Name'   : i['name'],
                    'Limit'  : i['limit'],
                    'volume' : volumes[str(i['id'])],
                    'id'     :i['id']
                   }
            except:
                pass
        return mapped

    def map_prices(self, volumes, prices):
        for i in prices:
            if int(i) not in volumes:
                continue
            try:
                volumes[int(i)].update({'high': prices[i]['high'], 'low': prices[i]['low']})
            except Exception as e:
                print("ouch", e, type(e.args))
                raise e
        return volumes

    def calc_margins(self, data):
        d = {}
        for i in data:
            buy     = data[i]['high']
            sell    = data[i]['low']
            margin  = buy - sell
            roi     = (buy * 100 / sell - 100).__round__(2)
            data[i].update({'margin': margin, 'roi': roi})
            d[i] =   data[i]
        return d

    def sort_roi_keys(self, data):
        a = sorted(data)
        return a

    def output_constraints(self, d):
        return d['volume'] > self.f_volume and d['high'] < self.f_high and d['low'] >= self.f_low and \
               d['margin'] > self.f_margin and d['roi'] > self.f_roi and \
               not any([x in d['Name'] for x in self.w_filter])

    def output(self, data):
        d = {}
        for i in data:
            d[data[i]['roi']] = data[i]

        roi_keys = self.sort_roi_keys(d)
        indx = 0
        output_data = {}

        for i in roi_keys:

            try:
                if not self.output_constraints(d[i]): continue
            except Exception as e:
                print(e)
            output_data.update({indx: {
                'Name'  : d[i]['Name'],
                'Margin': d[i]['margin'],
                'Buy'   : d[i]['low'],
                'Sell'  : d[i]['high'],
                'Pot'   : (d[i]['margin'] * d[i]['Limit']),
                'ROI'   : round(i, 1),
                'Limit' : d[i]['Limit'],
                'ID'    : str(d[i]['id'])
                    }
                })
            indx += 1

        self.pretty_print(output_data)
        return output_data

    def pretty_print(self, d):

        for i in d:
            print('\n')
            print(f"({i})  ROI: {d[i]['ROI']}  {d[i]['Name']} \n"
                  f"           Margin: {d[i]['Margin']:,}    Buy: {d[i]['Buy']:,}    Sell: {d[i]['Sell']:,}\n"
                  f"           Pot:    {d[i]['Margin'] * d[i]['Limit']:,}   Limit: {d[i]['Limit']}")

    def save_post(self, index):
        self.saved.update({index: self.data_cache[int(index)]})

    def remove_saved(self, index):
        del self.saved[index]

    def edit_constraints(self):
        print(f'Margin:     {self.f_margin}')
        print(f'Volume:     {self.f_volume}')
        print(f'High:       {self.f_high}')
        print(f'Low:        {self.f_low}')
        print(f'ROI:        {self.f_roi}')
        p = str(input('Enter constraint to edit: ')).lower()
        if p ==   'margin':
            self.f_margin   = int(input('New value: '))
        elif p == 'volume':
            self.f_volume   = int(input('New Value: '))
        elif p == 'high':
            self.f_high     = int(input('New Value: '))
        elif p == 'low':
            self.f_low      = int(input('New Value: '))
        elif p == 'roi':
            self.f_roi      = float(input('New Value: '))
        else:
            print('No value to edit')
        p = str(input('Edit more variables? Y/N')).lower()
        if p == 'y':
            self.edit_constraints()
        else:
            return

    def set_mode(self, i):
        self.scan_mode = "None"
        i = str(i)
        if i == '0':
            self.f_margin   = 5
            self.f_high     = 2000
            self.f_low      = 50
            self.f_volume   = 200000
            self.f_roi      = 0.3
            self.scan_mode       = "High Volume"
        if i == '1':
            self.f_margin   = 1000
            self.f_high     = 100000
            self.f_low      = 2000
            self.f_volume   = 25000
            self.f_roi      = 0.7
            self.scan_mode       = "Mid Volume"

        if i == '2':
            self.f_margin   = 10000
            self.f_high     = 22000000
            self.f_low      = 100000
            self.f_volume   = 500
            self.f_roi      = 2
            self.scan_mode       = "High Margin"
        if i == '9':
            self.scan_mode = "Custom"
            return self.edit_constraints()
        return self.scan_mode



    def update_savelist(self):

        p = self.get_prices()
        for i in self.saved:
            self.saved[i]['high']   = p['data'][self.saved[i]['ID']]['high']
            self.saved[i]['low']    = p['data'][self.saved[i]['ID']]['low']
        self.saved = self.calc_margins(self.saved)

if __name__ == '__main__':
    s = time.time()

    g = GEPrices()


    def main():
        volumes     = g.get_volumes()
        mappings    = g.get_mappings()
        volumes     = g.map_volumes(volumes, mappings)
        prices      = g.get_prices()
        data        = g.map_prices(volumes, prices['data'])
        data        = g.calc_margins(data)
        g.data_cache.update(g.output(data))


    def selector():

        selection = input("\n(1) Run Scan  (2) Save Result  (3) View Saved  (4) Remove Saved\n -> ")

        if selection   == '1':
            os.system("cls")
            main()
        elif selection == '2':
            g.save_post(int(input("index to save: ")))
        elif selection == '3':
            g.pretty_print(g.saved)
        elif selection == '4':
            g.remove_saved(int(input("index to remove: ")))
        elif selection == '5':
            print("(0) High Volume  (1) Mid Volume  (2) High Margin  (9) Custom\n")
            print(g.set_mode(input("-> ")))
        elif selection == '6':
            g.update_savelist()
        elif selection == '9':
            exit()


    while True:
        selector()
