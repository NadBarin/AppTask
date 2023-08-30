import sqlite3
class Database:
    def __init__(self):
        self.con = sqlite3.connect('todo.db')
        self.cursor = self.con.cursor()
        self.create_task_table()
    def create_task_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY, task varchar(50) NOT NULL, due_date varchar(50),complition_date varchar(50),parent_id integer, level integer, completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")
        self.con.commit()
    def create_task(self, task, due_date=None,parent_id=0, level=0, complition_date=None):
        self.cursor.execute("INSERT INTO tasks(task, due_date, complition_date, parent_id,level, completed) VALUES(?, ?, ?, ?, ?, ?)", (task, due_date,complition_date,parent_id,level, 0))
        self.con.commit()
    def get_tasks(self):
        tasks_view = self.cursor.execute("WITH RECURSIVE temp1 (id, task, due_date, complition_date, parent_id,level,completed) AS( SELECT t1.id, t1.task,t1.due_date,t1.complition_date, t1.parent_id, t1.level, t1.completed FROM tasks t1 WHERE t1.level=0 UNION ALL  SELECT t2.id, t2.task,t2.due_date,t2.complition_date, t2.parent_id, temp1.level+1, t2.completed FROM tasks t2 JOIN temp1 ON (temp1.id = t2.parent_id) ORDER BY 6 DESC) SELECT DISTINCT * FROM temp1 ").fetchall()
        # return the tasks to be added to the list when the application starts
        return tasks_view
    def mark_task_as_complete(self, taskid, comp_date):
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (taskid,))
        self.cursor.execute("UPDATE tasks SET complition_date=? WHERE id=?", (comp_date, taskid,))
        self.con.commit()
    def mark_task_as_incomplete(self, taskid):
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (taskid,))
        self.cursor.execute("UPDATE tasks SET complition_date=? WHERE id=?", (None, taskid,))
        self.con.commit()
        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (taskid,)).fetchall()
        return task_text[0][0]
    def delete_task(self, taskid):
        d = self.cursor.execute("SELECT COUNT(parent_id) FROM tasks WHERE parent_id!=0").fetchall()
        self.cursor.execute("DELETE FROM tasks WHERE id=? ", (taskid,))
        a = []
        for i in range(d[0][0]):
            a.extend(self.cursor.execute("SELECT id FROM tasks WHERE parent_id NOT IN (SELECT id FROM tasks) AND parent_id!=0").fetchall())
            #print(a)
            a = list(set(a))
            if (a != []):
                for j in a:
                    for i in range(len(j)):
                        self.cursor.execute("DELETE FROM tasks WHERE id=?", (j[i],))
        self.con.commit()
        return a
    def close_db_connection(self):
        self.con.close()