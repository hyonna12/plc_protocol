class SlotLayout:
    """슬롯 레이아웃 관리"""
    
    def __init__(self):
        # 슬롯 간격 (mm)
        self.GRID_WIDTH = 100   # x축 간격
        self.GRID_HEIGHT = 45  # z축 간격
        
        # 테이블 위치
        self.TABLE_POSITION = {"x": 0, "z": 0}
        
        # 슬롯 위치 매핑 초기화
        self.slot_positions = self._init_slot_positions()
        
    def _init_slot_positions(self):
        """슬롯 ID별 x, z 좌표 매핑 초기화"""
        positions = {}
        
        # 1~288: 후면(rear) 슬롯
        # 289~576: 전면(front) 슬롯
        SLOTS_PER_ROW = 24  # 한 줄당 슬롯 수
        
        for slot_id in range(1, 577):
            row = (slot_id - 1) // SLOTS_PER_ROW  # 행 번호
            col = (slot_id - 1) % SLOTS_PER_ROW   # 열 번호
            
            # x 좌표: 열 번호 * 간격
            x = col * self.GRID_WIDTH
            
            # z 좌표: 행 번호 * 간격
            z = row * self.GRID_HEIGHT
            
            positions[slot_id] = {"x": x, "z": z}
            
        return positions
        
    def get_position(self, slot_id: int) -> dict:
        """슬롯 ID에 해당하는 x, z 좌표 반환"""
        if slot_id == 0:  # 테이블
            return self.TABLE_POSITION
        # elif slot_id == -1:
        #     return self.DEFAULT_POSITION
        return self.slot_positions.get(slot_id)
        
    def is_front_slot(self, slot_id: int) -> bool:
        """전면 슬롯 여부 확인"""
        return slot_id > 288  # 289~576은 전면 