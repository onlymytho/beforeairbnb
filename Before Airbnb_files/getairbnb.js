

var result = {};

var enterinputexec = function(e) {
  if (e.which == 13 || e.keyCode == 13 || e.type == 'click') {
    ga('send', 'event', 'user_action_search', 'search', document.getElementsByClassName('where-is-your-airbnb')[0].value);


    console.log("Start to call listing information");
    var host_url = 'https://hplfmoc09e.execute-api.us-east-1.amazonaws.com/dev/before-airbnb-dev-get-results?x-api-key=uMM6O9xrIJ6f12Fcf9uos7aPCxSBBWKLmdKVAslc&location=' + document.getElementsByClassName('where-is-your-airbnb')[0].value;
    console.log(host_url)
    getJSON(host_url, callback_handling);
    document.getElementsByClassName('total_result_layout_container')[0].style.display = 'none';
    document.getElementsByClassName('analysis_result_layout_container')[0].style.display = 'none';
    document.getElementsByClassName('loading')[0].style.display = 'flex';
    document.getElementsByClassName('loading-giphy')[0].style.display = 'flex';
    var giphy_search = ['cute+cat', 'cute+corgi']
    var s_rand = Math.floor(Math.random() * 2);
    getJSON('http://api.giphy.com/v1/gifs/search?q='+giphy_search[s_rand]+'&api_key=dc6zaTOxFJmzC', giphy_callback);


    var counter = 15;
    var id;

    id = setInterval(function() {
        counter--;
        if(counter < 0) {
            clearInterval(id);
            if (userLang=='ko' || 'ko-kr'){
              document.getElementsByClassName('loading')[0].innerText = document.getElementsByClassName('where-is-your-airbnb')[0].value + ' 검색중...\n잠시만 기다려주세요';
              document.getElementsByClassName('loading')[0].style.textAlign = 'center';
            }
            else {
              document.getElementsByClassName('loading')[0].innerText = 'Searching for ' + document.getElementsByClassName('where-is-your-airbnb')[0].value + '...\nAlmomst done';
              document.getElementsByClassName('loading')[0].style.textAlign = 'center';
            }
        } else {
            if (userLang=='ko' || 'ko-kr'){
              document.getElementsByClassName('loading')[0].innerText = document.getElementsByClassName('where-is-your-airbnb')[0].value + ' 검색중...\n' + counter.toString() + '초 남았습니다.';
              document.getElementsByClassName('loading')[0].style.textAlign = 'center';
            }
            else {
              document.getElementsByClassName('loading')[0].innerText = 'Searching for ' + document.getElementsByClassName('where-is-your-airbnb')[0].value + '...\n' + counter.toString() + ' seconds left';
              document.getElementsByClassName('loading')[0].style.textAlign = 'center';
            }
        }
      }, 1000);



  }
  else {
    return false;
  }
};


var giphy_callback = function(err, giphy_data) {
  if (err != null) {
    console.log('Something went wrong: ' + err);
  }
  else {
    console.log(giphy_data);
    var rand = Math.floor(Math.random() * 24);
    document.getElementsByClassName('loading-giphy')[0].innerHTML = '<img class="giphy" src='+ giphy_data.data[rand].images.fixed_width.url + ' alt="Cute Giphy ">'
    rand = Math.floor(Math.random() * 24);
    document.getElementsByClassName('last-giphy')[0].innerHTML = '<img class="giphy" src='+ giphy_data.data[rand].images.fixed_width.url + ' alt="Cute Giphy ">'

  }
};



var callback_handling = function(err, data) {
  if (err != null) {
    alert('Something went wrong: ' + err);
  }
  else {
    result = data;
    console.log(data);
    // input interation
    document.getElementsByClassName('total_result_layout_container')[0].style.display = 'flex';
    document.getElementsByClassName('analysis_result_layout_container')[0].style.display = 'flex';
    document.getElementsByClassName('loading')[0].style.display = 'none';
    document.getElementsByClassName('loading-giphy')[0].style.display = 'none';

    if (userLang=='ko' || 'ko-kr'){

      // total score
      document.getElementsByClassName('a82')[0].innerText = data.total.score;
      document.getElementsByClassName('not-easy-but-there')[0].innerText = data.total.message.ko;

      // listing count and price analysis
      document.getElementById('price-statistics').innerText = '가격 분석';
      document.getElementsByClassName('avg-med-min-max')[0].innerText = '평균\n                중간\n                최소\n                최대';
      document.getElementsByClassName('a929-listings')[0].innerText = numberWithCommas(data.price.len) + '개의 에어비엔비';
      document.getElementsByClassName('prices')[0].innerText = numberWithCommas(data.price.avg)+'\n'+numberWithCommas(data.price.med)+'\n'+numberWithCommas(data.price.min)+'\n'+numberWithCommas(data.price.max);
      document.getElementById('price_statistics_desc').innerText = '평균 가격은 '+numberWithCommas(data.price.avg*1100)+'원입니다. 기본적으로 경쟁력을 확보하려면 '+numberWithCommas(data.price.min*1100)+'원에서 '+numberWithCommas(data.price.med*1100)+'원 사이가 적당한 가격일 것입니다. 만약 프리미엄 고객을 노리고 있다면 '+numberWithCommas(data.price.med*1100)+'원에서 '+numberWithCommas(data.price.max*1100)+'원 사이가 적당한 가격입니다.';


      // room_type analysis
      document.getElementById('room_type_statistics').innerText = '방 종류 분석';
      document.getElementById('room_type_statistics_desc').innerText = '많은 경쟁자들이 '+data.room_type.top+'형태의 방을 많이 소유하고 있습니다. 하지만 이와 관계 없이 당신이 제공할 수 있는 최고의 경험을 위한 방 형태를 준비해보세요.';
      document.getElementsByClassName('entire-home')[0].innerText = '집 전체';
      document.getElementsByClassName('private-room')[0].innerText = '개인방';
      document.getElementsByClassName('else')[0].innerText = '기타';

      document.getElementsByClassName('a726')[0].innerText = numberWithCommas(data.room_type.entire_home.price.len);
      document.getElementsByClassName('a191')[0].innerText = numberWithCommas(data.room_type.private_room.price.len);
      document.getElementsByClassName('a12')[0].innerText = numberWithCommas(data.room_type.else.price.len);
      document.getElementsByClassName('entire_home_prices')[0].innerText = numberWithCommas(data.room_type.entire_home.price.avg)+'\n'+numberWithCommas(data.room_type.entire_home.price.med)+'\n'+numberWithCommas(data.room_type.entire_home.price.min)+'\n'+numberWithCommas(data.room_type.entire_home.price.max);
      document.getElementsByClassName('private_room_prices')[0].innerText = numberWithCommas(data.room_type.private_room.price.avg)+'\n'+numberWithCommas(data.room_type.private_room.price.med)+'\n'+numberWithCommas(data.room_type.private_room.price.min)+'\n'+numberWithCommas(data.room_type.private_room.price.max);
      document.getElementsByClassName('else_prices')[0].innerText = numberWithCommas(data.room_type.else.price.avg)+'\n'+numberWithCommas(data.room_type.else.price.med)+'\n'+numberWithCommas(data.room_type.else.price.min)+'\n'+numberWithCommas(data.room_type.else.price.max);

      // super_host analysis
      document.getElementById('super_host_rate').innerText = '슈퍼 호스트 비율';
      document.getElementById('super_host_desc').innerText = data.super_host.message.ko;
      document.getElementById('super_host_label_first').innerText = '슈퍼 호스트';
      document.getElementById('super_host_label_last').innerText = '일반 호스트';
      document.getElementsByClassName('Opportunity')[0].innerText = '기회';

      document.getElementById('super_host_data_first').innerText = data.super_host.rate + '%';
      document.getElementById('super_host_data_last').innerText = 100-data.super_host.rate + '%';;
      document.getElementById('super_host_graph_body_first').style.width = data.super_host.rate + '%';
      document.getElementById('super_host_graph_body_last').style.width = 100-data.super_host.rate + '%';

      // business_travel analysis
      document.getElementById('business_preferred_rate').innerText = '비즈니스 여행 선호 비율';
      document.getElementById('business_preferred_desc').innerText = data.business_travel.message.ko;
      document.getElementById('business_preferred_label_first').innerText = '비즈니스 여행\n선호';
      document.getElementById('business_preferred_label_last').innerText = '비즈니스 여행\n비선호';
      document.getElementsByClassName('Opportunity')[1].innerText = '기회';

      document.getElementById('business_preferred_data_first').innerText = data.business_travel.rate + '%';
      document.getElementById('business_preferred_data_last').innerText = 100-data.business_travel.rate + '%';;
      document.getElementById('business_preferred_graph_body_first').style.width = data.business_travel.rate + '%';
      document.getElementById('business_preferred_graph_body_last').style.width = 100-data.business_travel.rate + '%';

      // family_preferred analysis
      document.getElementById('family_preferred_rate').innerText = '가족 여행 선호 비율';
      document.getElementById('family_preferred_desc').innerText = data.family_preferred.message.ko;
      document.getElementById('family_preferred_label_first').innerText = '가족 여행\n선호';
      document.getElementById('family_preferred_label_last').innerText = '가족 여행\n비선호';
      document.getElementsByClassName('Opportunity')[2].innerText = '기회';

      document.getElementById('family_preferred_data_first').innerText = data.family_preferred.rate + '%';
      document.getElementById('family_preferred_data_last').innerText = 100-data.family_preferred.rate + '%';
      document.getElementById('family_preferred_graph_body_first').style.width = data.family_preferred.rate + '%';
      document.getElementById('family_preferred_graph_body_last').style.width = 100-data.family_preferred.rate + '%';

      // Extra host langauage analysis
      document.getElementById('extra-host-languages').innerText = '제 2외국어 능력 비율';
      var list_keys = Object.keys(data.extra_host_language.list);
      var list_values = Object.values(data.extra_host_language.list);
      var rate_values = Object.values(data.extra_host_language.rate);
      for (var num=1; num<8; num++){
        document.getElementById('ex-lang' + num + '-graph').style.height = rate_values[num-1] + 'px';
        document.getElementById('ex-lang' + num + '-label').innerText = list_values[num-1].toUpperCase();
        document.getElementById('ex-lang' + num + '-rate').innerText = rate_values[num-1] + '%';
        document.getElementById('ex-lang' + num + '-rate').style.bottom = 29+6+rate_values[num-1] + 'px';
        };

      // Listings distances analysis
      document.getElementById('listings-distances').innerText = '거리에 따른 방 수';
      document.getElementById('distance').innerText = '거리';
      document.getElementById('count').innerText = '개수';
      document.getElementById('count-10').innerText = numberWithCommas(data.distance[10]) + '개';
      document.getElementById('count-20').innerText = numberWithCommas(data.distance[20]) + '개';
      document.getElementById('count-50').innerText = numberWithCommas(data.distance[50]) + '개';
      document.getElementById('count-100').innerText = numberWithCommas(data.distance[100]) + '개';
      document.getElementById('count-200').innerText = numberWithCommas(data.distance[200]) + '개';
      document.getElementById('count-300').innerText = numberWithCommas(data.distance[300]) + '개';
      document.getElementById('count-500').innerText = numberWithCommas(data.distance[500]) + '개';
      document.getElementById('count-1000').innerText = numberWithCommas(data.distance[1000]) + '개';
      document.getElementById('count-2000').innerText = numberWithCommas(data.distance[2000]) + '개';
      document.getElementById('count-3000').innerText = numberWithCommas(data.distance[3000]) + '개';

      // Listings distances analysis
      // var table = document.getElementsByClassName("listings-distances-table")[0];
      // var num = 0;
      //
      // for (d in result.distance) {
      //   var tr = table.insertRow(-1);
      //   tr.insertCell(-1).innerHTML = Object.keys(d)[num];
      //   tr.insertCell(-1).innerHTML = Object.values(d)[num];
      //   num = num + 1;
      //   }
      }
    else {
      // total score
      document.getElementsByClassName('a82')[0].innerText = data.total.score;
      document.getElementsByClassName('not-easy-but-there')[0].innerText = data.total.message.en;

      // listing count and price analysis
      document.getElementsByClassName('a929-listings')[0].innerText = data.price.len + ' listings';
      document.getElementsByClassName('a192682510216')[0].innerText = data.price.avg+'\n'+data.price.med+'\n'+data.price.min+'\n'+data.price.max;
      document.getElementById('price_statistics_desc').innerText = 'Median price is $'+data.price.med+'. To ensure competity, between $'+data.price.min+' and $'+data.price.med+' would be reasonable. If you are targeting to premium, between $'+data.price.med+' and $'+data.price.max+' would works.';

      // room_type analysis
      document.getElementById('room_type_statistics_desc').innerText = 'Many listings are concentrated to '+data.room_type.top+' type. You can avoid the type, but I recommend you to select room type you can provide the best.';
      document.getElementsByClassName('a726')[0].innerText = data.room_type.entire_home.price.len;
      document.getElementsByClassName('a191')[0].innerText = data.room_type.private_room.price.len;
      document.getElementsByClassName('a12')[0].innerText = data.room_type.else.price.len;
      document.getElementsByClassName('entire_home_prices')[0].innerText = data.room_type.entire_home.price.avg+'\n'+data.room_type.entire_home.price.med+'\n'+data.room_type.entire_home.price.min+'\n'+data.room_type.entire_home.price.max;
      document.getElementsByClassName('private_room_prices')[0].innerText = data.room_type.private_room.price.avg+'\n'+data.room_type.private_room.price.med+'\n'+data.room_type.private_room.price.min+'\n'+data.room_type.private_room.price.max;
      document.getElementsByClassName('else_prices')[0].innerText = data.room_type.else.price.avg+'\n'+data.room_type.else.price.med+'\n'+data.room_type.else.price.min+'\n'+data.room_type.else.price.max;

      // super_host analysis
      document.getElementById('super_host_desc').innerText = data.super_host.message.en;

      document.getElementById('super_host_data_first').innerText = data.super_host.rate + '%';
      document.getElementById('super_host_data_last').innerText = 100-data.super_host.rate + '%';
      document.getElementById('super_host_graph_body_first').style.width = data.super_host.rate + '%';
      document.getElementById('super_host_graph_body_last').style.width = 100-data.super_host.rate + '%';

      // business_travel analysis
      document.getElementById('business_preferred_desc').innerText = data.business_travel.message.en;

      document.getElementById('business_preferred_data_first').innerText = data.business_travel.rate + '%';
      document.getElementById('business_preferred_data_last').innerText = 100-data.business_travel.rate + '%';
      document.getElementById('business_preferred_graph_body_first').style.width = data.business_travel.rate + '%';
      document.getElementById('business_preferred_graph_body_last').style.width = 100-data.business_travel.rate + '%';

      // family_preferred analysis
      document.getElementById('family_preferred_desc').innerText = data.family_preferred.message.en;

      document.getElementById('family_preferred_data_first').innerText = data.family_preferred.rate + '%';
      document.getElementById('family_preferred_data_last').innerText = 100-data.family_preferred.rate + '%';
      document.getElementById('family_preferred_graph_body_first').style.width = data.family_preferred.rate + '%';
      document.getElementById('family_preferred_graph_body_last').style.width = 100-data.family_preferred.rate + '%';

      // Extra host langauage analysis
      var list_keys = Object.keys(data.extra_host_language.list);
      var list_values = Object.values(data.extra_host_language.list);
      var rate_values = Object.values(data.extra_host_language.rate);
      for (var num=1; num<7; num++){
        document.getElementById('ex-lang' + num + '-graph').style.height = rate_values[num-1] + 'px';
        document.getElementById('ex-lang' + num + '-label').innerText = list_values[num-1];
        document.getElementById('ex-lang' + num + '-rate').innerText = rate_values[num-1] + '%';
        document.getElementById('ex-lang' + num + '-rate').style.bottom = 29+5+rate_values[num-1] + 'px';

        };

      // Listings distances analysis
      document.getElementById('count-10').innerText = numberWithCommas(data.distance[10]);
      document.getElementById('count-20').innerText = numberWithCommas(data.distance[20]);
      document.getElementById('count-50').innerText = numberWithCommas(data.distance[50]);
      document.getElementById('count-100').innerText = numberWithCommas(data.distance[100]);
      document.getElementById('count-200').innerText = numberWithCommas(data.distance[200]);
      document.getElementById('count-300').innerText = numberWithCommas(data.distance[300]);
      document.getElementById('count-500').innerText = numberWithCommas(data.distance[500]);
      document.getElementById('count-1000').innerText = numberWithCommas(data.distance[1000]);
      document.getElementById('count-2000').innerText = numberWithCommas(data.distance[2000]);
      document.getElementById('count-3000').innerText = numberWithCommas(data.distance[3000]);
      // Listings distances analysis
      // var table = document.getElementsByClassName("listings-distances-table")[0];
      // var num = 0;
      //
      // for (d in result.distance) {
      //   var tr = table.insertRow(-1);
      //   tr.insertCell(-1).innerHTML = Object.keys(d)[num];
      //   tr.insertCell(-1).innerHTML = Object.values(d)[num];
      //   num = num + 1;
      //   }

      }

    }
  };
console.log(result)
