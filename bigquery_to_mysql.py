import mysql.connector
from google.oauth2 import service_account
from config import GOOGLE_APPLICATION_CREDENTIALS, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import pandas as pd
from datetime import datetime
import time

def bigquery_to_mysql():
    # Set up BigQuery client
    # Create credentials using the service account key JSON file
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)

    # Define your BigQuery SQL query here
    query = "SELECT * FROM `annular-moon-361814.Quests.ALL_quests`"

    # Read Google Big Query as Dataframe format
    t1 = time.time()
    df = pd.read_gbq(query, project_id='annular-moon-361814', credentials=credentials)

    # Get Points Data from the file
    points = pd.read_csv('quest_points/quest_points_new.csv')

    # Fill null values with 0
    df.fillna(0, inplace=True)

    # Change datatype of spent_agold column to float
    df.spent_agold = df.spent_agold.astype('float')

    # Index player column
    df.set_index('player', inplace=True)

    # Creating a key
    dt = datetime.now()
    day = dt.weekday() + 1
    week = dt.isocalendar().week

    # Getting points foreach column foreach player
    quest_points = {}
    temp = []
    old_name = ""
    for row in range(len(points.index)):
        if old_name != points.at[row, "name"]:
            if old_name != "":
                quest_points[old_name] = temp
            temp = []
            old_name = points.at[row, "name"]
        temp.append((points.iat[row, 2], points.iat[row, 3]))
        if(row == len(points.index) -1):
            quest_points[old_name] = temp
    
    # Function that returns player points
    def get_points(name, player_points):
        p = quest_points[name]
        ret = 0
        for values in p:
            if player_points >= values[1]:
                ret += values[0]
                continue
            return ret
    
    # Creating a copy of dataframe data
    result = df.copy()
    cols = len(df.columns)
    rows = len(df.index)

    # Get points foreach row/column
    for row in range(rows):
        for col in range(cols):
            p_a = df.iat[row, col]
            if(p_a > 0):
                result.iat[row, col] = get_points(df.columns[col ], p_a)

    # Get sum of points foreach row
    df['Points']=df.sum(axis='columns')

    # Get actions for each row
    df['Actions']=df.astype(bool).sum(axis=1)

    # Set key foreach row
    df['Key'] = str(day) + "-" + str(week)

    # Order rows based on points value DESC
    df = df.sort_values('Points', ascending=False)

    # Setting the position for each row
    df['Position'] = df['Points'].rank(method='dense', ascending=False).astype(int)

    # Get current time and put on created_at column for each row
    df['created_at'] = datetime.now()

    batch_size = 20000

    # Set up MySQL connection
    mysql_conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    mysql_cursor = mysql_conn.cursor()

    try:
        values = [(player, float(ixt_speedup_hours), float(gold_badge), float(silver_badge), float(bronze_badge), float(genesis_drone), float(piercer_drone),float(y_ms),float(lc_ms),float(gg_ms),float(ne_ms),float(nl_ms),float(hb_ms),float(gws_ms),float(el_ms),float(night_drone),float(spent_agold),float(arcades_owned),float(meta_mod_burn),float(silver_badge_burn),float(bronze_badge_burn),float(energy_burn),float(aoc_badge_pack_burn),float(aoc_badge_burn),float(cd3_burn),float(avatar_burn),float(minted_facilities),float(genesis_unique_mints),float(genesis_unique_owned),float(month_1),float(month_3),float(month_6),float(month_12),float(lp_usd_staked),float(regular_raffle),float(premium_raffle),float(golden_raffle),float(piercer_rover),float(genesis_rover),float(night_rover),float(la_minted),float(ls_minted),float(lz_minted),float(ld_minted),float(ra_minted),float(rs_minted),float(rz_minted),float(rd_minted),float(ua_minted),float(us_minted),float(uz_minted),float(ud_minted),float(ca_minted),float(cs_minted),float(cz_minted),float(cd_minted),float(oa_minted),float(os_minted),float(oz_minted),float(od_minted),float(la_owned),float(ls_owned),float(lz_owned),float(ld_owned),float(ra_owned),float(rs_owned),float(rz_owned),float(rd_owned),float(ua_owned),float(us_owned),float(uz_owned),float(ud_owned),float(ca_owned),float(cs_owned),float(cz_owned),float(cd_owned),float(oa_owned),float(os_owned),float(oz_owned),float(od_owned),float(waste_collected),float(energy_collected),float(prospecting_orders),float(gws_orders), int(position), created_at) for player, ixt_speedup_hours, gold_badge, silver_badge, bronze_badge, genesis_drone,piercer_drone,y_ms,lc_ms,gg_ms,ne_ms,nl_ms,hb_ms,gws_ms,el_ms,night_drone,spent_agold,arcades_owned,meta_mod_burn,silver_badge_burn,bronze_badge_burn,energy_burn,aoc_badge_pack_burn,aoc_badge_burn,cd3_burn,avatar_burn,minted_facilities,genesis_unique_mints,genesis_unique_owned,month_1,month_3,month_6,month_12,lp_usd_staked,regular_raffle,premium_raffle,golden_raffle,piercer_rover,genesis_rover,night_rover,la_minted,ls_minted,lz_minted,ld_minted,ra_minted,rs_minted,rz_minted,rd_minted,ua_minted,us_minted,uz_minted,ud_minted,ca_minted,cs_minted,cz_minted,cd_minted,oa_minted,os_minted,oz_minted,od_minted,la_owned,ls_owned,lz_owned,ld_owned,ra_owned,rs_owned,rz_owned,rd_owned,ua_owned,us_owned,uz_owned,ud_owned,ca_owned,cs_owned,cz_owned,cd_owned,oa_owned,os_owned,oz_owned,od_owned,waste_collected,energy_collected,prospecting_orders,gws_orders,position, created_at in zip(df.index, df["ixt_speedup_hours"], df["gold_badge"], df["silver_badge"], df["bronze_badge"], df["genesis_drone"],df["piercer_drone"],df["y_ms"], df["lc_ms"], df["gg_ms"], df["ne_ms"],df["nl_ms"],df["hb_ms"],df["gws_ms"],df["el_ms"],df["night_drone"],df["spent_agold"],df["arcades_owned"],df["meta_mod_burn"],df["silver_badge_burn"],df["bronze_badge_burn"],df["energy_burn"],df["aoc_badge_pack_burn"],df["aoc_badge_burn"],df["cd3_burn"],df["avatar_burn"],df["minted_facilities"],df["genesis_unique_mints"],df["genesis_unique_owned"],df["month_1"],df["month_3"],df["month_6"],df["month_12"],df["lp_usd_staked"],df["regular_raffle"],df["premium_raffle"],df["golden_raffle"],df["piercer_rover"],df["genesis_rover"],df["night_rover"],df["la_minted"],df["ls_minted"],df["lz_minted"],df["ld_minted"],df["ra_minted"],df["rs_minted"],df["rz_minted"],df["rd_minted"],df["ua_minted"],df["us_minted"],df["uz_minted"],df["ud_minted"],df["ca_minted"],df["cs_minted"],df["cz_minted"],df["cd_minted"],df["oa_minted"],df["os_minted"],df["oz_minted"],df["od_minted"],df["la_owned"], df["ls_owned"],df["lz_owned"],df["ld_owned"], df["ra_owned"], df["rs_owned"], df["rz_owned"], df["rd_owned"],df["ua_owned"], df["us_owned"],df["uz_owned"],df["ud_owned"],df["ca_owned"],df["cs_owned"],df["cz_owned"], df["cd_owned"], df["oa_owned"], df["os_owned"], df["oz_owned"], df["od_owned"], df["waste_collected"],df["energy_collected"],df["prospecting_orders"], df["gws_orders"], df["Position"], df["created_at"])]
        sql = "INSERT INTO player_points (player,ixt_speedup_hours,gold_badge,silver_badge,bronze_badge,genesis_drone,piercer_drone,y_ms,lc_ms,gg_ms,ne_ms,nl_ms,hb_ms,gws_ms,el_ms,night_drone,spent_agold,arcades_owned,meta_mod_burn,silver_badge_burn,bronze_badge_burn,energy_burn,aoc_badge_pack_burn,aoc_badge_burn,cd3_burn,avatar_burn,minted_facilities,genesis_unique_mints,genesis_unique_owned,month_1,month_3,month_6,month_12,lp_usd_staked,regular_raffle,premium_raffle,golden_raffle,piercer_rover,genesis_rover,night_rover,la_minted,ls_minted,lz_minted,ld_minted,ra_minted,rs_minted,rz_minted,rd_minted,ua_minted,us_minted,uz_minted,ud_minted,ca_minted,cs_minted,cz_minted,cd_minted,oa_minted,os_minted,oz_minted,od_minted,la_owned,ls_owned,lz_owned,ld_owned,ra_owned,rs_owned,rz_owned,rd_owned,ua_owned,us_owned,uz_owned,ud_owned,ca_owned,cs_owned,cz_owned,cd_owned,oa_owned,os_owned,oz_owned,od_owned,waste_collected,energy_collected,prospecting_orders,gws_orders,position, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ixt_speedup_hours = VALUES(ixt_speedup_hours), gold_badge = VALUES(gold_badge), silver_badge = VALUES(silver_badge), bronze_badge = VALUES(bronze_badge), genesis_drone = VALUES(genesis_drone), piercer_drone = VALUES(piercer_drone), y_ms = VALUES(y_ms), lc_ms = VALUES(lc_ms), gg_ms = VALUES(gg_ms), ne_ms = VALUES(ne_ms), nl_ms = VALUES(nl_ms), hb_ms = VALUES(hb_ms), gws_ms = VALUES(gws_ms), el_ms = VALUES(el_ms), night_drone = VALUES(night_drone), spent_agold = VALUES(spent_agold), arcades_owned = VALUES(arcades_owned), meta_mod_burn = VALUES(meta_mod_burn), silver_badge_burn = VALUES(silver_badge_burn), energy_burn = VALUES(energy_burn), aoc_badge_pack_burn = VALUES(aoc_badge_pack_burn), aoc_badge_burn = VALUES(aoc_badge_burn), cd3_burn = VALUES(cd3_burn), avatar_burn = VALUES(avatar_burn), minted_facilities = VALUES(minted_facilities), genesis_unique_mints = VALUES(genesis_unique_mints), genesis_unique_owned = VALUES(genesis_unique_owned), month_1 = VALUES(month_1), month_3 = VALUES(month_3), month_6 = VALUES(month_6), month_12 = VALUES(month_12), lp_usd_staked = VALUES(lp_usd_staked), regular_raffle = VALUES(regular_raffle), premium_raffle = VALUES(premium_raffle), golden_raffle = VALUES(golden_raffle), piercer_rover = VALUES(piercer_rover), genesis_rover = VALUES(genesis_rover), night_rover = VALUES(night_rover), la_minted = VALUES(la_minted), ls_minted = VALUES(ls_minted), lz_minted = VALUES(lz_minted), ld_minted = VALUES(ld_minted), ra_minted = VALUES(ra_minted), rs_minted = VALUES(rs_minted), rz_minted = VALUES(rz_minted), rd_minted = VALUES(rd_minted), ua_minted = VALUES(ua_minted), us_minted = VALUES(us_minted), uz_minted = VALUES(uz_minted), ud_minted = VALUES(ud_minted), ca_minted = VALUES(ca_minted), cs_minted = VALUES(cs_minted), cz_minted = VALUES(cz_minted), cd_minted = VALUES(cd_minted), oa_minted = VALUES(oa_minted), os_minted = VALUES(os_minted), oz_minted = VALUES(oz_minted), od_minted = VALUES(od_minted), waste_collected = VALUES(waste_collected), energy_collected = VALUES(energy_collected), prospecting_orders = VALUES(prospecting_orders), gws_orders = VALUES(gws_orders), position = VALUES(position),  created_at = VALUES(created_at);"
        for i in range(0, len(values), batch_size):
            batch = values[i:i+batch_size]
            mysql_cursor.executemany(sql, batch)
            mysql_conn.commit()

    except mysql.connector.Error as error:
        print("Failed to insert record into table {}".format(error))
        mysql_conn.rollback()
        if mysql_conn.is_connected():
            mysql_conn.close()
    finally:
        if mysql_conn.is_connected():
            mysql_conn.close()

    if not mysql_conn.is_connected():
        mysql_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        mysql_cursor = mysql_conn.cursor()
        try:
            stats = [(player, float(points), int(actions), str(key), created_at) for player, points, actions, key, created_at in zip(df.index, df['Points'], df['Actions'], df['Key'], df['created_at'])]
            sql2 = "INSERT INTO player_stats (player, points, actions, `key`, created_at) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE points = VALUES(points), actions = VALUES(actions), `key` = VALUES(`key`), created_at = VALUES(created_at)"
            for i in range(0, len(stats), batch_size):
                batch = stats[i:i+batch_size]
                mysql_cursor.executemany(sql2, batch)
                mysql_conn.commit()
        except mysql.connector.Error as error:
            print("Failed to insert record into table {}".format(error))
            mysql_conn.rollback()
            if mysql_conn.is_connected():
                mysql_conn.close()
        finally:
            if mysql_conn.is_connected():
                mysql_conn.close()

    else: 
        try:
            stats = [(player, float(points), int(actions), str(key), created_at) for player, points, actions, key, created_at in zip(df.index, df['Points'], df['Actions'], df['Key'], df['created_at'])]
            sql2 = "INSERT INTO player_stats (player, points, actions, `key`, created_at) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE points = VALUES(points), actions = VALUES(actions), `key` = VALUES(`key`), created_at = VALUES(created_at)"
            for i in range(0, len(stats), batch_size):
                batch = stats[i:i+batch_size]
                mysql_cursor.executemany(sql2, batch)
                mysql_conn.commit()
        except mysql.connector.Error as error:
            print("Failed to insert record into table {}".format(error))
            mysql_conn.rollback()
            if mysql_conn.is_connected():
                mysql_conn.close()
        finally:
            if mysql_conn.is_connected():
                mysql_conn.close()

    # Commit and close the MySQL connection
    mysql_cursor.close()
    mysql_conn.close()
    print(f"Final time {((time.time() - t1) / 60):.2f} minutes.")

if __name__ == "__main__":
    bigquery_to_mysql()
