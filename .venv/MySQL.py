# import pymysql
#
# class AverageForce:
#     def __init__(self):
#         try:
#             #self.db = pymysql.connect(host='localhost', user='jjm', password='q1w2e3', db='tmp')
#             self.db = pymysql.connect(host='localhost', user='root', password='j13051557', db='rehap')
#             self.cur = self.db.cursor()
#             print("Database connection established")
#         except pymysql.MySQLError as e:
#             print("Database connection failed:", e)
#
#     def saveForce(self, force):
#         sql = "INSERT INTO average_force (force_value) VALUES (%s)"
#         if not force.isdigit():  # force가 숫자가 아니면 오류 메시지 반환
#             print("Invalid force value:", force)
#             return
#         try:
#             self.cur.execute(sql, (force,))
#             self.db.commit()
#             print("Force value saved:", force)
#         except Exception as e:
#             print("Error while saving force:", e)
#             self.db.rollback()
#
#     def getHistory(self):
#         try:
#             sql = f"SELECT * FROM average_force"
#             self.cur.execute(sql)
#             return self.cur.fetchall()
#         except pymysql.MySQLError as e:
#             print("Database connection failed:", e)
#
#
# class TrainingManager:
#     def __init__(self):
#         #self.db = pymysql.connect(host='localhost', user='jjm', password='q1w2e3', db='tmp')
#         self.db = pymysql.connect(host='localhost', user='root', password='j13051557', db='rehap')
#         self.cur = self.db.cursor()
#
#     def setReps(self, sets, reps, rest):
#         sql = f"insert into combined_strength_and_sets (sets,reps,rest) values({sets},{reps},{rest})"
#         self.cur.execute(sql)
#         self.db.commit()