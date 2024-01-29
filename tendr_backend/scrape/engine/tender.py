import math
import re
import time

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from tendr_backend.common.utils.helper import datetime_parser
from tendr_backend.scrape.engine.aws_s3 import upload_to_s3
from tendr_backend.scrape.models import CftFile, ClientInfo, Tender

# def download_file(url, destination):
#     try:
#         local_path = f"{settings.MEDIA_ROOT}/{destination}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             with open(local_path, "wb") as file:
#                 file.write(response.content)
#             print(f"File downloaded successfully to {destination}")
#             upload_to_s3(local_path, destination)
#             return f"https://tendr.s3.eu-west-1.amazonaws.com/{destination}"
#         else:
#             print(f"Failed to download file. Status code: {response.status_code}")
#             return None
#     except Exception as e:
#         print(e)
#         return None


def download_file(url, destination):
    try:
        local_path = f"{settings.MEDIA_ROOT}/{destination}"
        with requests.get(url, stream=True) as response:
            if response.status_code == 200:
                with open(local_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive chunks
                            file.write(chunk)
                print(f"File downloaded successfully to {destination}")
                upload_to_s3(local_path, destination)
                return f"https://tendr.s3.eu-west-1.amazonaws.com/{destination}"
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
                return None
    except Exception as e:
        print(e)
        return None


def get_cft_file(resource_id):
    try:
        request_url = f"https://www.etenders.gov.ie/epps/cft/listContractDocuments.do?d-5419-p=&resourceId={resource_id}&T02_ps=100"  # noqa
        resp = requests.get(request_url)
        soup = BeautifulSoup(resp.content, features="html.parser")
        cft_files = []
        tbody = soup.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                columns = row.find_all("td")
                if columns:
                    addendum_id = columns[0].text.strip()
                    title = columns[1].text.strip()
                    document = columns[2].find("a") if columns[2].find("a") else None
                    if document:
                        document_id = re.search(r"\d+", document.get("onclick")).group()
                        document_type = document.text.strip().split(".")[-1]
                        file = download_file(
                            f"https://www.etenders.gov.ie/epps/cft/downloadContractDocument.do?documentId={document_id}",  # noqa
                            f"cft-files/{document_id}.{document_type}",
                        )
                    description = columns[3].text.strip()
                    lang = columns[4].text.strip()
                    doument_version = (
                        f"/epps/cft/viewDocumentVersions.do?resourceId={resource_id}&d-16398-p=&T02_ps=100"
                    )
                    action = f"/epps/cft/viewContractDocument.do?resourceId={resource_id}&contractDocID={document_id}"
                try:
                    cft_file = CftFile.objects.create(
                        addendum_id=addendum_id,
                        title=title,
                        file=file,
                        description=description,
                        lang=lang,
                        doument_version=doument_version,
                        action=action,
                    )
                    cft_files.append(cft_file)
                except Exception as e:
                    try:
                        cft_file = CftFile.objects.get(file=file)
                        cft_files.append(cft_file)
                    except Exception as e:
                        print(e)
                    print(e)
            time.sleep(1)
        return cft_files
    except Exception as e:
        print(e)


def get_client_info(info_url):
    try:
        request_url = f"https://www.etenders.gov.ie{info_url}"  # noqa
        resp = requests.get(request_url)
        soup = BeautifulSoup(resp.content, features="html.parser")
        table = soup.find("dl", attrs={"class": "row no-gutters"})
        dt_elements = table.find_all("dt")
        if len(dt_elements) == 12:
            organisation_name = dt_elements[0].find_next("dd").text.strip()
            ca_abbreviation = dt_elements[1].find_next("dd").text.strip()
            ca_type = dt_elements[2].find_next("dd").text.strip()
            annex = dt_elements[3].find_next("dd").text.strip()
            address = dt_elements[4].find_next("dd").text.strip()
            eircode_or_postal_code = dt_elements[5].find_next("dd").text.strip()
            city = dt_elements[6].find_next("dd").text.strip()
            county = dt_elements[7].find_next("dd").text.strip()
            email = dt_elements[8].find_next("dd").text.strip()
            phone_number = dt_elements[9].find_next("dd").text.strip()
            fax = dt_elements[10].find_next("dd").text.strip()
            website = dt_elements[11].find_next("dd").text.strip()
            try:
                client_info = ClientInfo(
                    organisation_name=organisation_name,
                    ca_abbreviation=ca_abbreviation,
                    ca_type=ca_type,
                    annex=annex,
                    address=address,
                    eircode_or_postal_code=eircode_or_postal_code,
                    city=city,
                    county=county,
                    email=email,
                    phone_number=phone_number,
                    fax=fax,
                    website=website,
                )
                return client_info
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return None


def get_tender_detail(detail_url):
    try:
        request_url = f"https://www.etenders.gov.ie{detail_url}"
        resp = requests.get(request_url)
        soup = BeautifulSoup(resp.content, features="html.parser")
        table = soup.find("dl", attrs={"class": "row no-gutters"})
        if table:
            dt_elements = table.find_all("dt")
            data_dict = {}
            for dt in dt_elements:
                dt_text = re.sub(r"_+$", "", re.sub(r"[^\w]+", "_", dt.text.strip().lower()))
                if dt.find_next("dd").find("a"):
                    if dt.find_next("dd").find("a", href=lambda href: href and "https://ted" in href):
                        dd_text = dt.find_next("dd").find("a")["href"]
                    else:
                        info_url = dt.find_next("dd").find("a")["href"]
                        dd_text = dt.find_next("dd").find("a").text.strip()
                        client_info = get_client_info(info_url)
                else:
                    dd_text = dt.find_next("dd").text.strip().replace("\r", "").replace("\t", "")
                data_dict[dt_text] = dd_text
            return (data_dict, client_info)
    except Exception as e:
        print(e)

    return (None, None)


def main(page: int):
    try:
        request_url = f"https://www.etenders.gov.ie/epps/viewCFTSFromFTSAction.do?estimatedValueMax=&contractType=&publicationUntilDate=&cpvLabels=&description=&procedure=&title=&tenderOpeningUntilDate=&cftId=&contractAuthority=&mode=search&cpcCategory=&submissionUntilDate=&estimatedValueMin=&publicationFromDate=&submissionFromDate=&d-3680175-p={page}&tenderOpeningFromDate=&T01_ps=100&uniqueId=&status="  # noqa
        resp = requests.get(request_url)
        print(resp.status_code)
        soup = BeautifulSoup(resp.content, features="html.parser")
        table = soup.find("table", attrs={"id": "T01"})
        # tenders = []
        print("page", page)
        if table is not None:
            for row in table.find("tbody").find_all("tr"):
                columns = row.find_all("td")
                if columns:
                    title = columns[1].find("a").text.strip()
                    detail_url = columns[1].find("a")["href"]
                    resource_id = columns[2].text.strip()
                    try:
                        Tender.objects.get(resource_id=resource_id)
                        continue
                    except Exception as e:
                        print(e)
                    ca = columns[3].text.strip()
                    info = columns[4].find("img")["title"].strip()
                    date_published = columns[5].text.strip()
                    tenders_submission_deadline = columns[6].text.strip()
                    procedure = columns[7].text.strip()
                    status = columns[8].text.strip()
                    notice_pdf_link = columns[9].find("a")["href"] if columns[9].find("a") else None
                    if notice_pdf_link:
                        notice_pdf = download_file(
                            f"https://www.etenders.gov.ie{notice_pdf_link}", f"notice-pdfs/{resource_id}.pdf"
                        )
                    else:
                        notice_pdf = None
                    award_date = columns[10].text.strip()
                    estimated_value = columns[11].text.strip()
                    try:
                        estimated_value = float(estimated_value)
                    except Exception as e:
                        print(e)
                        estimated_value = None
                    cycle = columns[12].text.strip()
                    tender_detail, client_info = get_tender_detail(detail_url)
                    cft_files = get_cft_file(resource_id)
                    tender = Tender(
                        title=title,
                        resource_id=resource_id,
                        ca=ca,
                        info=info,
                        date_published=datetime_parser(date_published),
                        tenders_submission_deadline=tenders_submission_deadline,
                        procedure=procedure,
                        status=status,
                        notice_pdf=notice_pdf,
                        award_date=award_date,
                        estimated_value=estimated_value,
                        cycle=cycle,
                        tender_detail=tender_detail,
                        cpv_code=tender_detail["cpv_codes"]
                        # "cft_files": cft_files,
                    )
                    tender.save()

                    if cft_files:
                        for cft_file in cft_files:
                            tender.cft_files.add(cft_file)
                    if client_info is not None:
                        client_info.tendr_id = tender
                        client_info.save()
    except Exception as e:
        print(e)


def get_resource_id():
    resource_ids = []
    try:
        request_url = f"https://www.etenders.gov.ie/epps/viewCFTSFromFTSAction.do?estimatedValueMax=&contractType=&publicationUntilDate=&cpvLabels=&description=&procedure=&title=&tenderOpeningUntilDate=&cftId=&contractAuthority=&mode=search&cpcCategory=&submissionUntilDate=&estimatedValueMin=&publicationFromDate=&submissionFromDate=&d-3680175-p={1}&tenderOpeningFromDate=&T01_ps=100&uniqueId=&status="  # noqa
        resp = requests.get(request_url)
        print(resp.status_code)
        soup = BeautifulSoup(resp.content, features="html.parser")
        total_number = int("".join(re.findall(r"\d+", re.findall("1-100(.+)results in total", soup.text)[0])))
        total_page_number = math.ceil(total_number / 100)
        table = soup.find("table", attrs={"id": "T01"})
        # tenders = []
        # print("page", page)
        if table is not None:
            for row in table.find("tbody").find_all("tr"):
                columns = row.find_all("td")
                if columns:
                    resource_id = columns[2].text.strip()
                    resource_ids.append(resource_id)
        for page in range(2, total_page_number + 1):
            request_url = f"https://www.etenders.gov.ie/epps/viewCFTSFromFTSAction.do?estimatedValueMax=&contractType=&publicationUntilDate=&cpvLabels=&description=&procedure=&title=&tenderOpeningUntilDate=&cftId=&contractAuthority=&mode=search&cpcCategory=&submissionUntilDate=&estimatedValueMin=&publicationFromDate=&submissionFromDate=&d-3680175-p={page}&tenderOpeningFromDate=&T01_ps=100&uniqueId=&status="  # noqa
            resp = requests.get(request_url)
            print(resp.status_code)
            soup = BeautifulSoup(resp.content, features="html.parser")
            table = soup.find("table", attrs={"id": "T01"})
            if table is not None:
                for row in table.find("tbody").find_all("tr"):
                    columns = row.find_all("td")
                    if columns:
                        resource_id = columns[2].text.strip()
                        resource_ids.append(resource_id)
        return (resource_ids, total_page_number)

    except Exception as e:
        print(e)
