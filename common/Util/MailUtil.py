from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import os


class EmailContent:
    def __init__(self, senderAdr, emailSubject, toReceivers, ccReceivers):
        # 邮件对象
        self.msg = MIMEMultipart()
        # 添加发件人头
        self.msg['From'] = Header("美股" + "<" + senderAdr + ">", 'utf-8')
        # 添加收件人
        if isinstance(toReceivers, str):
            self.msg["To"] = toReceivers
        elif isinstance(toReceivers, list):
            self.msg['To'] = ";".join(toReceivers)
        # 添加抄送人
        if isinstance(ccReceivers, str):
            self.msg["Cc"] = ccReceivers
        elif isinstance(ccReceivers, list):
            self.msg["Cc"] = ";".join(ccReceivers)
        # 添加邮件主题
            self.msg['Subject'] = Header(emailSubject, "utf-8")

    def addBody(self, bodyType, body):
        """
        添加不同的邮件正文的实例
        1. body为字符串：(如)"这是一个邮件正文内容"
        2. body为html格式的字符串：(如)"<div><p>第一段</p><p>&nbsp;第二段</p></div>"
        3. body正文中包含有图片：
        """
        if bodyType == "string":
            mimeText = MIMEText(body, "plain", "utf-8")
            self.msg.attach(mimeText)
        elif bodyType == "html":
            mimeText = MIMEText(body, "html", "utf-8")
            self.msg.attach(mimeText)
        elif "image" in bodyType:
            imageFile = "E://log//test.png"
            imageId = os.path.split(imageFile)[1]
            mimeText = MIMEText(body, "html", "utf-8")
            self.msg.attach(mimeText)
            # 读取图片，并设置图片id用于邮件正文引用
            with open(imageFile, "rb") as fp:
                mimeImage = MIMEImage(fp.read())
            mimeImage.add_header("Content-ID", imageId)
            self.msg.attach(mimeImage)

    def addAttachment(self, attachmentName):
        file = "E://log//test.txt"
        # file = "E://log//test.zip"
        # file = "E://log//test.png"
        filePath, fileName = os.path.split(file)
        print("fileName =", fileName)
        enclosure = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
        enclosure['Content-Type'] = 'application/octet-stream'
        if attachmentName == "英文":
            enclosure['Content-Disposition'] = 'attachment; filename="%s"' % fileName
        elif attachmentName == "中文":
            enclosure.add_header("Content-Disposition", "attachment", filename=("gbk", "", fileName))
        self.msg.attach(enclosure)



def SendEmail(title, content):
    """发送邮件"""
    # SMTP的服务器信息
    smtpHost = "smtp.qq.com"
    sslPort = 465   
    senderAdr = "1498053401@qq.com"
    senderPwd = "ldtqfnqxmjasfjac"
    # 创建SMTP对象
    smtpServer = smtplib.SMTP_SSL(smtpHost, sslPort)
    # # 设置debug模块
    # smtpServer.set_debuglevel(True)
    # 登录
    smtpServer.login(senderAdr, senderPwd)
    # 添加邮件内容
    # toReceivers = ['1498053401@qq.com', '470415096@qq.com']
    toReceivers = ['1498053401@qq.com']
    ccReceivers = []
    emailContent = EmailContent(senderAdr, title, toReceivers, ccReceivers)
    emailContent.addBody("string", content)
    message = emailContent.msg
    # 发送
    smtpServer.sendmail(senderAdr, toReceivers, message.as_string())
    # 终止SMTP会话
    smtpServer.quit()