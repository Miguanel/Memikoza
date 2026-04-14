import json
import datetime
from scrapps import get_jbzd, get_jmonster, get_kwejks, get_demot, get_redmik, get_atomgrab


class MemMenager():
    def __init__(self):
        self.data: dict = {}
        self.memy = {}
        self.refresh_time_limit = 900
        self.memjson = 'mems.json'

    def fresh_mems(self, npt, seconds=10):
        # Format daty jako string zapobiega błędom TypeError przy json.dumps w innych plikach
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "last_used" in self.memy.keys():
            last_used_dt = datetime.datetime.strptime(self.memy["last_used"], "%Y-%m-%d %H:%M:%S")
            deltatime = datetime.datetime.now() - last_used_dt
            if deltatime.seconds < seconds:
                return False

        self.memy = {}
        self.npt = npt

        self.memy.update(self.get_jbzd())
        self.memy.update(self.get_jmonster())
        self.memy.update(self.get_demot())
        self.memy.update(self.get_kwejks())
        self.memy.update(self.get_redmik())
        self.memy.update(self.get_atomgrab())

        # Zapisujemy sformatowany string
        self.memy.update({"last_used": now_str})
        return True

    def get_jbzd(self):
        return get_jbzd(self.npt["jbzd_limit"])

    def get_jmonster(self):
        return get_jmonster(self.npt["jm_limit"])

    def get_kwejks(self):
        return get_kwejks(self.npt["kw_limit"])

    def get_demot(self):
        return get_demot(self.npt["dm_limit"])

    def get_redmik(self):
        return get_redmik(self.npt["rm_limit"])

    def get_atomgrab(self):
        return get_atomgrab(self.npt["ag_limit"])

    def mem_refresh(self, npt):
        memy = {}
        memy.update(self.get_jbzd())
        memy.update(self.get_jmonster())
        memy.update(self.get_demot())
        memy.update(self.get_kwejks())
        memy.update(self.get_redmik())
        memy.update(self.get_atomgrab())
        return memy

    def save_mems_to_file(self):
        with open(self.memjson, 'w') as json_file:
            json.dump(self.memy, json_file)

    def load_mems_from_json(self):
        try:
            with open(self.memjson) as jf:
                temp = json.load(jf)
                self.data.update(temp)
                return True
        except Exception as e:
            print(f"load_mems_from_json: {e}")
            return False