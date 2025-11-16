HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real Estate API</title>
    <!-- 1. โหลด Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 2. ตั้งค่าฟอนต์ที่สวยงาม (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">

    <!-- 3. การ์ดต้อนรับตรงกลาง -->
    <div class="bg-white p-10 md:p-12 rounded-xl shadow-2xl text-center max-w-lg mx-4">
        
        <!-- ไอคอนบ้าน (SVG) -->
        <svg class="w-20 h-20 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>

        <!-- หัวเรื่อง -->
        <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mt-6">
            Welcome to the Real Estate API
        </h1>
        
        <!-- คำอธิบาย -->
        <p class="text-gray-600 mt-3 text-lg">
            A modern API for managing and retrieving real estate data.
        </p>
        
        <!-- 4. ปุ่มที่สำคัญที่สุด: ลิงก์ไปยัง /docs -->
        <a href="/docs" 
           class="mt-8 inline-block px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:bg-blue-700 transition-colors duration-300">
            View API Documentation
        </a>
    </div>

</body>
</html>
"""