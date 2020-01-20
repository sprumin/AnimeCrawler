from bs4 import BeautifulSoup

import requests



def get_anime(url):
	animes = list()
	res = BeautifulSoup(requests.get(url).content, 'html.parser')
	html = res.find_all("tr", {"class": "array"})

	for row in html:
		rank = row.find("td", {"class": "rank"}).text
		# 이미지 다운로드 링크임 나중에 S3쓰면 연동해줌
		image = row.find("td", {"class": "thumb"}).img['data-original']
		link = row.find("td", {"class": "maintitle"}).a['href']
		title = row.find("td", {"class": "maintitle"}).text
		category = row.find("td", {"class": "category"}).text
		date = row.find("td", {"class": "date"}).text

		# rank diff 에서 순위 + - 는 배포전에 아래 링크 참고해서 미리 다운로드받고 보여줄떄 아래 이미지로 표기할것
		# 순위변동 없음 ex) <img src="//member.onnada.com/_/img/real_stop.gif"><span>{{ rank_diff }}</span>
		# 순위 올라감 ex) <img src="//member.onnada.com/_/img/real_up.gif"><span>{{ rank_diff }}</span>
		# 순위 내려감 ex) <img src="//member.onnada.com/_/img/real_down.gif"><span>{{ rank_diff }}</span>
		rank_diff = row.find("td", {"class": "move pointer"}).text

		# 애니메이션 상세 정보 
		anime_detail = get_anime_detail(link)
		
		# 아래 get_anime_detail의 return값과 아래 animes에 append할 내용이 겹칠 수 있음.
	    # 그러나 아래 date보다 get_anime_detail에서 가져온 date가 더 상세함.
	    # 결론은 key는 같아도 value는 다르다는거 ㅇㅇ 물론 "detail"에 들어갈 value가 더 상세함.
		animes.append({
			"rank": rank,
			"image": image,
			"link": link,
			"title": title,
			"category": category,
			"date": date,
			"rank_diff": rank_diff,
			"detail": anime_detail
		})

	return animes


def get_anime_detail(url):
	# 사실 쉽게 끝날 줄 알았는데 저 사이트 개같이 만들어져서 쉽게못함
	# 어쩜 저렇지?
	# 거지같은거 때문에 아래 dictionary 작성함
	default_words = {
		"원제": "original_title",
		"원작": "original_anime",
		"감독": "director",
		"각본": "screen_writer",
		"캐릭터 디자인": "char_design",
		"음악": "music",
		"제작사": "company",
		"장르": "category",
		"분류": "class",
		"키워드": "keyword",
		"제작국가": "country",
		"방영일": "date",
		"등급": "film_rating",
		"총화수": "total_episode",
		"공식홈페이지": "homepage",
		"공식트위터": "twitter"
	}
	detail = dict()
	res = BeautifulSoup(requests.get(url).content, 'html.parser')
	html = res.find("div", {"class": "list"}).find_all("span", {"class": "block"})

	for i in range(len(html)):
		if i % 2 == 0:
			detail[default_words[html[i].text]] = None
		else:
			detail[default_words[html[i-1].text]] = html[i].text
	
	return detail 


def lambda_handler(event, context):
	url = "http://anime.onnada.com/rank.php"
	all_anime = get_anime(url)
	
	print(all_anime[0])