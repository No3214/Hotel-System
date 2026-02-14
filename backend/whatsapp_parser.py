import re
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WhatsAppParser:
    """Parse WhatsApp export messages and extract actionable items"""
    
    @staticmethod
    def parse_export_file(content: str) -> Dict[str, Any]:
        """
        Parse WhatsApp export text file
        Format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
        """
        messages = []
        
        # Regex patterns for WhatsApp messages
        pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)'
        
        lines = content.split('\n')
        current_message = None
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                # New message
                date_str, time_str, sender, text = match.groups()
                
                # Save previous message
                if current_message:
                    messages.append(current_message)
                
                # Start new message
                current_message = {
                    'date': date_str,
                    'time': time_str,
                    'sender': sender.strip(),
                    'text': text.strip()
                }
            elif current_message and line.strip():
                # Continuation of previous message
                current_message['text'] += ' ' + line.strip()
        
        # Add last message
        if current_message:
            messages.append(current_message)
        
        return {
            'total_messages': len(messages),
            'messages': messages,
            'unique_senders': list(set(msg['sender'] for msg in messages))
        }
    
    @staticmethod
    def extract_orders(messages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract orders from WhatsApp messages
        Örnek: "50 adet yumurta lazım", "yarın organik yumurta 50 adet"
        """
        orders = []
        
        # Keywords for orders
        order_keywords = ['sipariş', 'lazım', 'gerek', 'al', 'getir', 'bul', 'adet', 'kilo', 'litre']
        
        for msg in messages:
            text_lower = msg['text'].lower()
            
            # Check if message contains order keywords
            if any(keyword in text_lower for keyword in order_keywords):
                # Extract quantity and item
                quantity_match = re.search(r'(\d+)\s*(adet|kilo|kg|litre|lt|gram)', text_lower)
                
                order = {
                    'sender': msg['sender'],
                    'date': msg['date'],
                    'time': msg['time'],
                    'message': msg['text'],
                    'quantity': None,
                    'unit': None,
                    'category': 'order'
                }
                
                if quantity_match:
                    order['quantity'] = int(quantity_match.group(1))
                    order['unit'] = quantity_match.group(2)
                
                orders.append(order)
        
        return orders
    
    @staticmethod
    def extract_requests(messages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract action requests from messages
        Örnek: "oda 5'i hazırla", "kahvaltı saat 8'de"
        """
        requests = []
        
        # Keywords for requests
        request_keywords = ['hazırla', 'yap', 'kontrol et', 'bak', 'gönder', 'ara', 'bildir', 'söyle']
        
        for msg in messages:
            text_lower = msg['text'].lower()
            
            if any(keyword in text_lower for keyword in request_keywords):
                # Extract time if present
                time_match = re.search(r'(\d{1,2})[:.]?(\d{2})?\s*(de|da|te|ta)?', text_lower)
                
                request = {
                    'sender': msg['sender'],
                    'date': msg['date'],
                    'time': msg['time'],
                    'message': msg['text'],
                    'action_time': None,
                    'category': 'request'
                }
                
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    request['action_time'] = f"{hour:02d}:{minute:02d}"
                
                requests.append(request)
        
        return requests
    
    @staticmethod
    def extract_complaints(messages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract complaints or issues
        Örnek: "bozuk", "çalışmıyor", "sorun var"
        """
        complaints = []
        
        # Keywords for complaints
        complaint_keywords = ['bozuk', 'çalışmıyor', 'sorun', 'problem', 'yok', 'eksik', 'kötü', 'kirli']
        
        for msg in messages:
            text_lower = msg['text'].lower()
            
            if any(keyword in text_lower for keyword in complaint_keywords):
                complaint = {
                    'sender': msg['sender'],
                    'date': msg['date'],
                    'time': msg['time'],
                    'message': msg['text'],
                    'priority': 'high',  # Complaints are high priority
                    'category': 'complaint'
                }
                complaints.append(complaint)
        
        return complaints
    
    @staticmethod
    def create_tasks_from_whatsapp(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create tasks from parsed WhatsApp data
        """
        tasks = []
        
        messages = parsed_data.get('messages', [])
        
        # Extract different types
        orders = WhatsAppParser.extract_orders(messages)
        requests = WhatsAppParser.extract_requests(messages)
        complaints = WhatsAppParser.extract_complaints(messages)
        
        # Create tasks for orders
        for order in orders:
            task = {
                'title': f"Sipariş: {order['message'][:50]}...",
                'description': order['message'],
                'source': 'whatsapp',
                'source_sender': order['sender'],
                'priority': 'normal',
                'category': 'order',
                'metadata': order
            }
            tasks.append(task)
        
        # Create tasks for requests
        for request in requests:
            task = {
                'title': f"Talep: {request['message'][:50]}...",
                'description': request['message'],
                'source': 'whatsapp',
                'source_sender': request['sender'],
                'priority': 'normal',
                'category': 'request',
                'metadata': request
            }
            if request.get('action_time'):
                task['due_time'] = request['action_time']
            tasks.append(task)
        
        # Create tasks for complaints
        for complaint in complaints:
            task = {
                'title': f"ÖNEMLİ: {complaint['message'][:50]}...",
                'description': complaint['message'],
                'source': 'whatsapp',
                'source_sender': complaint['sender'],
                'priority': 'high',
                'category': 'complaint',
                'metadata': complaint
            }
            tasks.append(task)
        
        return tasks

# Example usage
if __name__ == "__main__":
    sample_whatsapp = """
[14/02/2026, 08:30:15] Mehmet: 50 adet yumurta lazım yarına
[14/02/2026, 08:31:22] Ayşe: Tamam sipariş vereceğim
[14/02/2026, 09:15:43] Ahmet: Oda 5'in kliması bozuk, kontrol et
[14/02/2026, 10:20:18] Fatma: Kahvaltı saat 9'da hazır olsun yarın
[14/02/2026, 11:05:32] Mehmet: Organik yumurta olmalı mutlaka
    """
    
    parser = WhatsAppParser()
    parsed = parser.parse_export_file(sample_whatsapp)
    tasks = parser.create_tasks_from_whatsapp(parsed)
    
    print(f"Total messages: {parsed['total_messages']}")
    print(f"Tasks created: {len(tasks)}")
    for task in tasks:
        print(f"  - {task['title']} [{task['priority']}]")
