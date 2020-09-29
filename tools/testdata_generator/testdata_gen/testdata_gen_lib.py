# -*- coding: utf-8 -*-
# @Author  : xiang.wang
import json
import yaml
from functools import reduce
from itertools import chain, product
from addict import Dict
from collections import defaultdict
import collections
import operator
import copy
import random

from autotest.lib.allthepairs.all_pairs2 import all_pairs2 as all_pairs


def random_select_multiple_dict_items(d):
    return dict(random.sample(list(d.items()), random.randint(0, len(list(d.items())))))


def flatten_dict(d, parent_key='', sep='.', quiet=True):
    items = []
    for k, v in list(d.items()):

        if not quiet and sep in k:
            raise ValueError('Separator "%(sep)s" already in key, '
                             'this may lead unexpected behaviour, '
                             'choose another.' % dict(sep=sep))
        new_key = parent_key + sep + k if parent_key else k
        print(("new_key", new_key))
        if isinstance(v, collections.MutableMapping):
            items.extend(list(flatten_dict(v, new_key, sep=sep).items()))
            if not v:  # empty dict
                items.append((new_key, v))
        elif isinstance(v, collections.MutableSequence):
            if not v:  # empty list
                items.append((new_key, v))
            for index, i in enumerate(v):
                if isinstance(i, collections.MutableMapping):
                    items.extend(list(flatten_dict(i, new_key + str([index]), sep=sep).items()))
                # elif isinstance(i, collections.MutableSequence):
                # 	for index2, i2 in enumerate(i):
                #
                # TO DO: need to handle nest list scenario
                # 	print("nk", new_key)
                # 	print(3,i, index)

                else:
                    items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)


def generate_pairs(d, mode):
    # convert multiple-dimensional dictionary to one-dimensional dictionary
    d = flatten_dict(d)
    pairs = generate_multiple_dict_list(d, mode)
    lst = []
    for i in pairs:
        lst.append(convert_dotdict_to_dict(i))
    return lst


def get_parent_key(d, key):
    dot = flatten_dict(d)
    key_set = set()
    for i in list(dot.keys()):
        if '.' in i:
            key_lst = i.split('.')
            for ks in key_lst:
                if '[' in ks:
                    c_ks, _, _ = ks.rpartition('[')
                else:
                    c_ks = ks
                if c_ks == key:
                    index = i.index(ks)
                    key_set.add(i[:index].strip('.'))

        else:
            if key in i:
                if '[' in i:
                    c_i, _, _ = i.rpartition('[')
                else:
                    c_i = i
                if c_i == key:
                    key_set.add('')
                else:
                    pass

    return list(key_set)


def restructure_dict(d):
    for k, v in list(d.items()):
        new_value = d[k]
        if '[' in k:

            if isinstance(new_value, dict):
                new_value = restructure_dict(new_value)
            elif isinstance(new_value, list):
                new_value_list = []
                for i in new_value:
                    if isinstance(i, dict):
                        new_value_list.append(restructure_dict(i))
                new_value = new_value_list
            new_key = k.split('[')[0]
            d.pop(k)
            if new_key in d:
                pass
            else:
                d[new_key] = []
            d[new_key].append(new_value)
        else:
            if isinstance(new_value, dict):
                new_value = restructure_dict(new_value)
            new_key = k
            d[new_key] = new_value
    return d


def convert_dotdict_to_dict(d):
    infinitedict = lambda: defaultdict(infinitedict)
    new_d = infinitedict()
    for k, v in list(d.items()):
        if k.find('.') != -1:
            keys = k.split('.')
            last_key = keys[-1]
            rest_key = keys[:-1]
        else:
            keys = k
            last_key = k
            rest_key = []
        lastplace = reduce(operator.getitem, rest_key, new_d)
        lastplace[last_key] = v

    return restructure_dict(yaml.safe_load(json.dumps(new_d)))


# return restructure_dict(json.loads(json.dumps(new_d)))
# return restructure_dict(dict(new_d))

def combin_dict(*args):
    return reduce(lambda x, y: dict(chain(list(x.items()), list(y.items()))), args)


def generate_forms_config(forms_items):
    forms_config = {}
    tmp_d = {}
    del_lst = []
    dot = flatten_dict(forms_items)

    print(dot)

    for k, v in list(dot.items()):
        lr, mr, rr = k.partition('Required')
        lo, mo, ro = k.partition('Optional')
        if mr and not all([mr, mo]):
            del_lst.append(k)
            forms_config[lr.strip('.') + rr] = v
        if mo and not all([mr, mo]):
            del_lst.append(k)
            if 'condition' in k:
                forms_config[lo.strip('.') + ro] = v
            else:
                tmp_d[lo.strip('.') + ro] = v
        if all([mr, mo]):
            print(('should to handle ', k))
    list(map(dot.pop, del_lst))

    final_dict = Dict(convert_dotdict_to_dict(combin_dict(dot, forms_config, random_select_multiple_dict_items(tmp_d))))

    return final_dict


def del_dict_item(key, d):
    if isinstance(key, str):
        list(map(lambda x: x.pop(key), d))
    if isinstance(key, list):
        for i in key:
            list(map(lambda x: x.pop(i), d))


def update_dict_by_same_key(dict1, dict2):
    '''

    :param dict1: {"a":'', "b":'', "c":''}
    :param dict2: {"a":2, "d":"3"}
    :return: {"a":2, "b":'', "c":''}
    comments: update the dict1 base on the same key between dict1 and dict2,
    it"s different from dict(dict1, **dict2) (will return {"a":2, "b":'', "c":'', "d":3})
    '''

    dict1.update((k, dict2[k]) for k in set(dict2).intersection(dict1))
    return dict1


def generate_multiple_dict_list(d, mode):
    '''
    Generate new dict and append it to list when the key has list type values
    d = {u"accountBranch": "ab",
                                    u"accountNumber": "b",
                                    u"bankPayMode": [u"0", u"1"],
                                    u"city": "c",
                                    u"confirmAccountNumber": "d",
                                    u"financialInstitution": "e",
                                    u"province": "f"}

    list(all_pairs(d.values()))
==> [["f", "c", "b", u"0", "e", "a", "d"], ["f", "c", "b", u"1", "e", "a", "d"]]

    then use zip to generate new dict

    [{u"province": "f", u"city": "c", u"accountNumber": "b", u"bankPayMode": u"0",
    u"financialInstitution": "e", u"accountBranch": "ab", u"confirmAccountNumber": "d"},
    {u"province": "f", u"city": "c", u"accountNumber": "b", u"bankPayMode": u"1",
    u"financialInstitution": "e", u"accountBranch": "ab", u"confirmAccountNumber": "d"}]

    '''
    # filter new dict which has list type value

    filtered_dict = dict(
        [x for x in list(d.items()) if isinstance(
                x[1],
                list) and len(x[1]) > 0])
    # print filtered_dict.values()
    if filtered_dict:
        if len(filtered_dict) < 2:
            dict_list = [{list(filtered_dict.keys())[0]: x}
                         for x in list(filtered_dict.values())[0]]

        else:
            if mode in ["mini", "random"]:
                f_d = list(filtered_dict.values())
                try:
                    f_d.sort()
                except TypeError:
                    pass
                #d = all_pairs(f_d)
                dict_list = [dict(list(zip(list(filtered_dict.keys()), x))) for x in list(
                    all_pairs(f_d))]
            # all_pairs(list(filtered_dict.values()))))
            elif mode == "full":
                dict_list = [dict(list(zip(list(filtered_dict.keys()), x))) for x in list(
                    product(*list(filtered_dict.values())))]

        final_dict = [
            update_dict_by_same_key(
                copy.deepcopy(d),
                x) for x in dict_list]
    else:
        final_dict = [d]
    return final_dict


def random_select_testcase(forms_pairs):
    forms = {}
    for k, v in list(forms_pairs.items()):
        if isinstance(v, dict):
            # print v

            forms.update({k: v})
        elif isinstance(v, list):
            if len(v) > 0:
                lst = []
                for i in v:
                    if isinstance(i, dict):
                        forms.update({k: random.choice(v)})

                    if isinstance(i, list):
                        isdict = False
                        for x in i:
                            if isinstance(x, dict):
                                isdict = True
                            else:
                                isdict = False
                        if isdict:
                            diff_lst = [y for y in i if y not in lst]
                            if diff_lst:
                                lst.append(random.choice(diff_lst))
                            else:
                                lst.append(diff_lst)
                        forms.update({k: lst})
            else:
                forms.update({k: v})
    return forms


def testdata_gen(body, mode='mini'):
    t = generate_forms_config(body)
    pairs = generate_pairs(t, mode)
    if mode in ["mini", "full"]:
        pairs = pairs
    elif mode in ["random"]:
        pairs = random.choice(pairs)

    return pairs


if __name__ == '__main__':
    import pprint
    #
    #d = {"Required": {"a": "1", "b": ["1", "2", "3"], "c": {"d": {"e": [{"s": 1}, {"s": 2}]}}, "f": ["1", "2"]},
    #     "Optional": {"x": "1", "y": ["1", "2", "3"]}}
    # d = {"a":"1","b":["1","2","3"],"c":{"d":{"e":["1","2","3"]}}, "x":"1","y":["1","2","3"], "z":["1", "2"]}
    d = {
        "Required": {
            "a": "1",
            "b": [
                "1",
                "2",
                "3"
            ],
            "c": {
                "d": {
                    "e":
                        [
                            [{
                                "s1": [1, 4]
                            },
                                {
                                    "s2": 2
                                }
                            ], [{
                            "s3": 1
                        },
                            {
                                "s4": 2
                            }
                        ]]
                }
            },
            "f": [
                "1",
                "2"
            ]
        },
        "Optional": {
            "x": "1",
            "y": [
                "1",
                "2",
                "3"
            ]
        }
    }
    pairs = testdata_gen(d, 'full')
    pprint.pprint(pairs)
'''
    d = {"CRM_CREATED_SMB_finaceInfo": {"finance_personalHouse": "ZERO", "finance_loanBalance3": "87166",
                                        "finance_loanBalance2": "6401", "finance_loanBalance1": "91343",
                                        "finance_loanExpiredDate1": 43451979000,
                                        "finance_loanExpiredDate2": 334367878000,
                                        "finance_loanExpiredDate3": 1219726622000,
                                        "finance_nonbankInstitutionsNum": "TWO",
                                        "finance_applyFromOtherInstitutions": "YES", "finance_personalCar": "TWO",
                                        "finance_otherYearlyIncome": "4411"},
         "CRM_CREATED_SMB_company": {"company_totalIncome": "999508241", "company_applicantShare": "85",
                                     "company_telephoneExt": "999", "company_paidTaxState": "YES",
                                     "company_orgCodeCert": "2233262230498", "company_jobTitle": "Aid",
                                     "company_jobTenureYears": "9",
                                     "company_operationAddress": {"province": "湖北", "city": "武汉", "district": "历下",
                                                                  "detailedAddress": "聂路U座"},
                                     "company_totalCost": "805422078", "company_profit": "45",
                                     "company_businessLicenseNum": "9283733744378",
                                     "company_establishDate": 1080016387000, "company_name": "名字",
                                     "company_industryCode": "I005", "company_mortgageState": "YES",
                                     "company_lawsuitState": "NO", "company_telephone": "0435-98210565",
                                     "company_loanState": "YES", "company_size": "WORLD_500"},
         "CRM_CREATED_SMB_mortgage_guarantor": {"CRM_CREATED_SMB_guarantorPersonal": [],
                                                "CRM_CREATED_SMB_mortgageInfo": [{"mortgage_houseAddr": {
                                                    "province": "广西壮族自治区", "city": "南宁", "district": "历下",
                                                    "detailedAddress": "凌路q座"}, "mortgage_subtype": "HOUSE",
                                                                                  "mortgage_houseOwner": "韦淑英",
                                                                                  "mortgage_houseType": "OFFICE",
                                                                                  "mortgage_courtName": "富兰英",
                                                                                  "mortgage_houseStatus": "RENT",
                                                                                  "mortgage_mortgageTimes": "SECOND",
                                                                                  "mortgage_amt": 716902,
                                                                                  "mortgage_houseArea": 89,
                                                                                  "mortgage_provideSecondHouse": "YES",
                                                                                  "mortgage_relation": ["CHILDREN"],
                                                                                  "mortgage_hasMortgage": "YES",
                                                                                  "mortgage_landType": "OTHER",
                                                                                  "mortgage_remain": "YES",
                                                                                  "mortgage_houseBuyTime": "2003",
                                                                                  "mortgage_houseTotalAmt": 492368}],
                                                "CRM_CREATED_SMB_guarantorCorporate": []},
         "CRM_CREATED_SMB_loanApp": {"loan_remark": "备注信息", "loan_paymentMethod": "AMORTIZATION",
                                     "loan_appAmount": 1148700, "loan_purpose": "SUPPLY_CHAIN_RETAIL",
                                     "loan_description": "Quisquam suscipit quo a nihil sapiente sunt tenetur. Voluptate reiciendis quam labore excepturi optio quasi. Nulla nobis cumque ipsa iure officiis blanditiis minima. Quod excepturi odit porro quam.",
                                     "loan_channel": 11,
                                     "loan_title": "Cupiditate incidunt totam modi fugit nesciunt ipsa.",
                                     "loan_maturity": "MONTH_42"}, "CRM_CREATED_SMB_bankAccount": [
            {"bank_bankProvince": "上海", "bank_bankCity": "上海", "bank_bank": "中国银行", "bank_branch": "申路L座支行",
             "bank_accountNum": "6226090210427833", "bank_accountName": "名字", "bank_ownerType": "TRUSTEE"}],
         "CRM_CREATED_SMB_basicInfo": {"person_educationLevel": "UNGRADUATE", "person_paidTaxStatus": "NO",
                                       "person_residenceYearsLimit": "FROM_4_TO_6",
                                       "user_cardNum": "632322196402161538", "person_childrenStatus": "ZERO",
                                       "person_residenceAddr": {"province": "云南", "city": "昆明", "district": "历下",
                                                                "detailedAddress": "阳路y座"},
                                       "person_annualIncome": 411298, "person_wechat": "5506239055408",
                                       "person_houseStatus": "RENT", "person_maritalStatus": "DIVORCED",
                                       "person_mobilePhone": "15859250314", "CRM_CREATED_SMB_contact": [
                 {"contact_name": "配偶", "contact_cardNum": "130822198103272322", "contact_relation": "COUPLE"}],
                                       "user_realName": "名字"}}
    pairs = testdata_gen(d, 'full')
    pprint.pprint(pairs)
'''

