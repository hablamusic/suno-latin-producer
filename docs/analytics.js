/* Cookieless, anonymous page views for hablamusic.github.io only: no cookies, no storage, no person profile.
   Sends nothing on other hosts, in frames, or with Do Not Track / Global Privacy Control. PostHog EU, HablaMusic project. */
(function(){'use strict';var H='hablamusic.github.io',K='phc_qQsaL7gcjUjMJY59sQHQxUDiSAjBgqDBMZy7gAxaTv6J',E='https://eu.i.posthog.com/i/v0/e/',n=navigator;
if(location.hostname!==H)return;if(n.doNotTrack==='1'||n.globalPrivacyControl===true)return;try{if(window.top!==window.self)return}catch(x){return}
var site=location.pathname.split('/')[1]||'org';
function send(ev,p){try{var q={$process_person_profile:false,$lib:'gh-pages',site:'gh-'+site,$current_url:location.origin+location.pathname,$pathname:location.pathname,$referrer:document.referrer||'$direct',lang:document.documentElement.lang};for(var k in p)q[k]=p[k];var b=JSON.stringify({api_key:K,event:ev,distinct_id:'anon',properties:q});if(n.sendBeacon&&n.sendBeacon(E,new Blob([b],{type:'text/plain'})))return;fetch(E,{method:'POST',body:b,keepalive:true}).catch(function(){})}catch(x){}}
send('$pageview',{});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.href;if(h.indexOf('hablamusic.com')>-1||h.indexOf('github.com')>-1||h.indexOf('roimobi.com')>-1)send('outbound_click',{href:h.split('?')[0],text:(a.textContent||'').trim().slice(0,60)})},true);
document.addEventListener('tool_used',function(e){send('tool_used',e.detail||{})});
})();
