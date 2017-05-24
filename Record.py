from datetime import datetime

# 시간 기록 클래스. r.start()와 r.end()를 활용. 여러 개의 시간 기록들을 이용할 경우, 기록인자.r.start()와 기록인자.r.end() 이용
    # 아무 인자도 입력하지 않을 경우, 기본 기록인자인 t에 기록. 여러 개를 동시에 돌릴 경우 서로 엉킬 수 있음.
    # 여러 개의 record를 돌릴 경우, 특정 기록인자를 string으로 입력하면 해당 string이름으로 기록이 구분되어서 기록됨.


tracker = {}

def start(*args):
    '''
        # args : 기록인자(string)
        # 아무 인자도 입력하지 않을 경우, 기본 기록인자인 t에 기록. 여러 개를 동시에 돌릴 경우 서로 엉킬 수 있음.
        # 여러 개의 record를 돌릴 경우, 특정 기록인자를 string으로 입력하면 해당 string이름으로 기록이 구분되어서 기록됨.
    '''
    global trackers
    global t
    if args:
        for a in args:
            tracker[a] = datetime.now()
            print ("'" + str(a) + "'" + " started at " + str(tracker[a]))
    else:
        t = datetime.now()
        return t


def end(*args):
    '''
        # args : 기록인자(string)
        # 이전에 start함수를 불러온 적이 있을 때만 사용 가능.
        # 아무 인자도 입력하지 않을 경우, 기본 기록인자인 t에 대한 결과값을 불러옴. 여러 개를 동시에 돌릴 경우 서로 엉킬 수 있음.
        # 여러 개의 record를 돌릴 경우, 특정 기록인자를 string으로 입력하면 해당 string이름으로 기록이 구분되어서 기록됨.
        # n개의 함수를 실행하는 프로그램에서 처음 시작부터 각 단계까지 얼마까지 걸리고 있는지를 체크하려고 한다면 그냥 end함수를 계속 쓰면 됨. end 함수는 처음 값을 초기화하지 않기 때문에 start부터 end가 찍힌 부분까지의 시간을 기록함.
    '''
    if args:
        for a in args:
            end_time = datetime.now()
            d = end_time - tracker[a]
            print ("Duration for " + "'" + str(a) + "'" +  " : " + str(d))
    else:
        end = datetime.now()
        d = end - t
        print ("Duration : " + str(d))
