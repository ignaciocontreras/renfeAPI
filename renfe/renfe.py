import urllib, sqlite3
from bs4 import BeautifulSoup

class Renfe(object):
  def __init__(self):
    self.conn = sqlite3.connect('database')

  def get_ciudades(self):
    cursor = self.conn.cursor()
    cursor.execute('SELECT nucleo, ciudad FROM ciudades ORDER BY ciudad ASC')
    return cursor.fetchall()

  def get_estaciones(self, nucleo):
    cursor = self.conn.cursor()
    cursor.execute('SELECT id, estacion FROM estaciones WHERE nucleo=%s ORDER BY estacion ASC' % nucleo)
    return cursor.fetchall()

  def get_nucleo(self, estacion):
    cursor = self.conn.cursor()
    cursor.execute('SELECT c.nucleo FROM ciudades c, estaciones e WHERE c.nucleo=e.nucleo AND e.id=%s' % estacion)
    return cursor.fetchone()[0]

  def get_page(self, nucleo, orig, dest):
    url = 'http://horarios.renfe.com/cer/hjcer310.jsp'
    params = urllib.urlencode({
      'f1': '',
      'i': 's',
      'cp': 'NO',
      'nucleo': nucleo, # nucleo
      'o': orig, # estacion origen
      'd': dest, # estacion destino
      'df': 20130621, # dia en formato yyyymmdd
      'ho': 00, # hora de origen
      'hd': 26, # hora de destino
      'TXTInfo': ''})
    p = urllib.urlopen(url, params)
    return p.read()

  def parse_normal(self, table):
    list = []
    trs = self.get_trs(table)
    for tr in trs:
      td = self.get_tds(tr)
      obj = {}
      obj['linea'] = td[0].string
      obj['ho'] = td[1].string
      obj['hd'] = td[2].string
      obj['tiempo'] = td[3].string
      list.append(obj)
    return list

  def parse_transbordo(self, table):
    list = []
    trs = self.get_trs(table)
    tds = self.get_tds(trs)
    print tds
    return list

  def get_trs(self, table):
    trs = table.tr.td.find_all('tr') # devuelve un tr con muchos trs dentro
    del trs[0] # borrar primer td (donde esta la info)
    return trs

  def get_tds(self, tr):
    tds = tr.find_all('td')
    return tds

  def hay_transbordo(self, table):
    trs = self.get_trs(table)
    print trs
    tds = self.get_tds(trs[0])
    return len(tds) > 5

  def parse_page(self, html):
    html = BeautifulSoup(html)
    table = BeautifulSoup(str(html.table))
    list = []
    if self.hay_transbordo(table):
      print 'Hay transbordo'
      list = self.parse_transbordo(table)
    else:
      print 'No hay transbordo'
      list = self.parse_normal(table)
    return list

  def get_horarios(self, orig, dest):
    nucleoO = self.get_nucleo(orig)
    nucleoD = self.get_nucleo(dest)
    if nucleoO == nucleoD:
      page = self.get_page(nucleoO, orig, dest)
      return self.parse_page(page)

if __name__ == '__main__':
  r = Renfe()
  ciudades = r.get_ciudades()
  i = 0
  for ciudad in ciudades:
    # print i, ciudad
    i += 1
  # n = int(input('Select Ciudad: '))
  n = 1
  estaciones = r.get_estaciones(ciudades[n][0])
  i = 0
  for estacion in estaciones:
    # print i, estacion
    i += 1
  # n = int(input('Select Origen: '))
  n = 96 # sanfe
  origen = estaciones[n][0]
  # n = int(input('Select Destino: '))
  # n = 97 # sant joan
  n = 0 # aeroport
  destino = estaciones[n][0]
  horarios = r.get_horarios(origen, destino)
  if horarios:
    for horario in horarios:
      print horario
  else:
    print 'No he conseguido los horarios'
