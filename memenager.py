import json
import datetime
from scrapps import get_jbzd, get_jmonster, get_kwejks, get_demot, get_redmik, get_atomgrab

dtt = datetime.datetime.today


class MemMenager():

    def __init__(self):
        self.data: dict = {}
        self.memy = {}
        self.refresh_time_limit = 900
        self.memjson = 'mems.json'

    def fresh_mems(self, npt, seconds=10):
        if "last_used" in self.memy.keys():
            deltatime = dtt().today() - self.memy["last_used"]
            good_diff: bool = deltatime.seconds < seconds
            if good_diff:
                return False
        self.memy = {}
        self.npt = npt
        jb = self.get_jbzd()
        dj = self.get_jmonster()
        dm = self.get_demot()
        kw = self.get_kwejks()
        redmik = self.get_redmik()
        atomgrab = self.get_atomgrab()
        lus = {"last_used": dtt().today()}

        self.memy.update(jb)
        self.memy.update(dj)
        self.memy.update(dm)
        self.memy.update(kw)
        self.memy.update(redmik)
        self.memy.update(atomgrab)

        self.memy.update(lus)
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
        jb = self.get_jbzd()
        dj = self.get_jmonster()
        dm = self.get_demot()
        kw = self.get_kwejks()
        rm = self.get_redmik()
        ag = self.get_atomgrab()
        memy.update(jb)
        memy.update(dj)
        memy.update(dm)
        memy.update(kw)
        memy.update(rm)
        memy.update(ag)
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
            print(f"""load_mems_from_json: {e}""")
            return False
        finally:
            jf.close()

    def check_memy(self, npt):
        mmd = self.load_mems_from_json()
        if not mmd:  # first run
            mmd.update(self.mem_refresh(npt))
            self.save_mems_to_file(mmd)
            return
        rt = dtt()
        if rt.total_seconds() > self.refresh_time_limit:  # refresh mems
            self.mem_refresh(npt)
            return 'mems reloaded', dtt()

