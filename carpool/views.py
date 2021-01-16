from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from .form import AddJoinForm, AddPoolForm, SearchTimeForm, AddPlaceForm
from django.utils import timezone
import json
from django.views.decorators.http import require_POST
import datetime
# Create your views here.
from django.core import serializers

def check_delete(request):
    print(1)
    print(timezone.now())
    print(Pool.objects.filter(departure_date__lte=timezone.now()).exists())
    if Pool.objects.filter(departure_date__lte=timezone.now()).exists():
        print(11111)
        pol1 = Pool.objects.filter(departure_date__lte=timezone.now())
        for p in pol1:
            print(1111)
            list = p.profile_set.all()
            for li in list:
                print(li.user.username)
                li.load = None
                li.number = None
                li.status = 0
                li.save()

        Pool.objects.filter(departure_date__lte=timezone.now()).delete()

def carpool_home(request, place_id = None):
    #current_place도 만들어야 한다.
    place_list0 = []
    place_list = {'info': []}
    place_menu = Place.objects.all()
    place = Place.objects.all()
    pool = Pool.objects.all()
    check_msg = ''
    #print(Pool.objects.filter(departure_date__gte=timezone.now()).exists())
    check_delete(request)

    #for select pagination
    idx_min = 1
    idx_max = 4
    prev_off = 0
    next_off = 0
    #

    #Pool.objects.filter(
    #    number__lte = 0
    #).delete()

    #print(request.GET)
    dep_placeholder = []
    if 'from_date' in request.GET and 'to_date' in request.GET:
        form = SearchTimeForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['from_date'] < cd['to_date']:
                pool = pool.filter(departure_date__gte=cd['from_date'], departure_date__lte=cd['to_date'])
                dep_placeholder.append(cd['from_date'].strftime("%Y-%m-%d %H:%M"))
                dep_placeholder.append(cd['to_date'].strftime("%Y-%m-%d %H:%M"))

            else:
                check_msg = 'Invalid Input!'
    else:
        form = SearchTimeForm()

    search = request.GET.get('place_name', '')  # 이건 나중에 검색 후, dropdown의 메뉴 폭을 좁히는 데에 써야한다.
    if search:
        place_menu = place_menu.filter(name__icontains=search)

    cnt = 0
    for pl in place_menu:
        cnt += 1
        if cnt >= idx_min and cnt <= idx_max:
            place_list0.append(pl)
        place_list['info'].append({'id': pl.id, 'name': pl.name})


    if cnt <= idx_max:
        next_off = 1
    if idx_min == 1:
        prev_off = 1

    if place_id:
        place = place.filter(id=place_id)
        pool = pool.filter(place__in=place)

    my_var = {'pos': [], 'map_center':[36.01633, 129.321248]}
    pool_info = {'info': []}
    ovlap = {}
    gap = {0:[0.0001, 0], 1:[0, 0.0001], 2:[-0.0001, 0], 3:[0,-0.0001], 4:[0.00005,0.00005], 5:[-0.00005,0.00005], 6:[0.00005,-0.00005], 7:[-0.00005,-0.00005]}
    #nmad = []
    if place.count() == 1:
        pl = place.first()
        my_var['map_center'][0] = pl.latitude
        my_var['map_center'][1] = pl.longitude

    for pl in place:
        ovlap[pl.name] = 0
    for pol in pool:
        ovlap[pol.place.name] += 1

    for pol in pool:
        if ovlap[pol.place.name] > 1:
            pol.gap_lat = gap[(ovlap[pol.place.name] - 2) % 8][0] * ((ovlap[pol.place.name]-2)//8 + 1)
            pol.gap_lon = gap[(ovlap[pol.place.name] - 2) % 8][1] * ((ovlap[pol.place.name]-2)//8 + 1)

        my_var['pos'].append({'l1': pol.place.latitude + pol.gap_lat, 'l2': pol.place.longitude + pol.gap_lon})
        pool_info['info'].append({'name': pol.place.name, 'number': pol.number, 'load': pol.load, 'id': pol.id, 'departure_date':pol.departure_date.strftime("%Y-%m-%d \n %H:%M")})
        ovlap[pol.place.name] -= 1
        #nmad.append({'name': pl.name, 'address': pl.address})
    output = json.dumps(my_var)
    #names = json.dumps(name)

    is_auth = request.user.is_authenticated
    is_join = False
    if is_auth:
        user = User.objects.get(username=request.user)
        if user.profile.status > 0:
            is_join = True

    return render(request, 'carpool/carpool.html', {'places0':place_list0, 'places':place_list, 'idx_min':idx_min, 'prev_off':prev_off, 'next_off':next_off, 'dep_placeholder':dep_placeholder, 'is_auth':is_auth,'is_join':is_join, 'msg':check_msg, 'form': form, 'pools': pool, 'output':output, 'pool_info': pool_info})


def join_pool(request, pool_id):
    msg =''
    user = User.objects.get(username=request.user)
    profile = user.profile

    if request.method == "POST":
        form = AddJoinForm(request.POST)
        #cd = form.cleaned_data
        if form.is_valid():
            pool_sel = Pool.objects.get(id=pool_id)
            cd = form.cleaned_data
            if pool_sel.number + cd['number'] <= 4:
                pool_sel.number += cd['number']
                pool_sel.load += cd['load']
                pool_sel.save()

                profile.pool = pool_sel
                profile.load = cd['load']
                profile.number = cd['number']
                profile.status = 1
                profile.save()

                return redirect('carpool')
            else:
                msg = '가능 인원 수 초과 : 최대 {0}명까지 가능'.format(4-pool_sel.number)
    else:
        form = AddJoinForm()

    return render(request, 'carpool/join.html', {'form': form, 'msg': msg})


def add_pool(request):
    msg = ''
    user = User.objects.get(username=request.user)
    profile = user.profile
    place = Place.objects.all()
    if request.method == "POST":
        print('#1')
        form = AddPoolForm(request.POST)
        if form.is_valid():
            print('#2')
            cd = form.cleaned_data
            profile.pool = form.save()
            profile.load = cd['load']
            profile.number = cd['number']
            profile.status = 2
            profile.save()

            return redirect('carpool')
        else:
            print(form.errors['departure_date'])
            msg = " Departure date can't be in the past!"
            form = AddPoolForm(request.POST)
    else:
        form = AddPoolForm()

    return render(request, 'carpool/add.html', {'place':place, 'form':form, 'msg':msg})

def add_place(request):
    pool = Place.objects.all()
    pl = Place()
    msg = ' Place already exists!'
    err = 0
    if request.method == 'POST':

        try:
            exist = pool.filter(latitude = request.POST.get('latitude'), longitude =request.POST.get('longitude')).exists()
        except ValueError:
            err = 1;
            msg = ' Select a Place to add!'
            return render(request, 'carpool/place_add.html', {'msg': msg, 'error': err})

        if exist:
            err = 1;
            return render(request,'carpool/place_add.html',{'msg':msg, 'error':err})
        else:             
            pl.name=request.POST.get('name')
            pl.address =request.POST.get('address')
            pl.latitude=request.POST.get('latitude')
            pl.longitude = request.POST.get('longitude')
            pl.save()
            return redirect('carpool')
    return render(request, 'carpool/place_add.html', {'msg':'', 'error':err})

def account_info(request):
    if request.method == "POST":
        pk = request.POST.get('pk', None)
        content = request.POST.get('content', None)

        pol = Pool.objects.get(id=pk)
        pol.kakao_url = content
        pol.save()
        context = {'content': pol.kakao_url}
        return HttpResponse(json.dumps(context), content_type="application/json")

    check_delete(request)
    pol = Pool()
    user = User.objects.get(username=request.user)
    profile = user.profile
    status = profile.status
    members_profile = Profile()
    if status > 0:
        pol = profile.pool #이렇게 불러오는 게 맞나?
        members_profile = pol.profile_set.all()
    return render(request, 'carpool/account_info.html', {'members':members_profile, 'status':status, 'pol':pol})

def leave_confirm(request, pool_id):
    pol = Pool.objects.get(id = pool_id)
    user = User.objects.get(username=request.user)
    profile = user.profile

    if request.method == 'POST':
        pol.number -= profile.number
        pol.load -= profile.load
        pol.save()

        profile.pool = None
        profile.load = None
        profile.number = None
        profile.status = 0
        profile.save()

        return redirect('ac_info')
    return render(request, 'carpool/leave_confirm.html',{})

def delete_confirm(request, pool_id):
    pol = Pool.objects.get(id = pool_id)
    user = User.objects.get(username=request.user)
    profile = user.profile
    list = pol.profile_set.all()
    if request.method == 'POST':
        #print(request.POST)
        if list.count() > 1:
            auth = User.objects.get(username=request.POST['auth'])
            auth_pf = auth.profile
            auth_pf.status = 2
            auth_pf.save()
            pol.number -= profile.number
            pol.load -= profile.load
            pol.save()
        else:
            pol.delete()

        profile.pool = None
        profile.load = None
        profile.number = None
        profile.status = 0
        profile.save()

        return redirect('ac_info')
    return render(request, 'carpool/delete_confirm.html', {'cnt':list.count(), 'list': list})

