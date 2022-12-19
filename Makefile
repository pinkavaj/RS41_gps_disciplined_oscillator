TARGET = disc-osc

#TOOLCHAIN = ../toolchain/bin/
AS = $(TOOLCHAIN)arm-none-eabi-as
#LD = $(TOOLCHAIN)arm-none-eabi-ld
LD = $(TOOLCHAIN)arm-none-eabi-gcc
CC = $(TOOLCHAIN)arm-none-eabi-gcc
OC = $(TOOLCHAIN)arm-none-eabi-objcopy
OD = $(TOOLCHAIN)arm-none-eabi-objdump
OS = $(TOOLCHAIN)arm-none-eabi-size

ASFLAGS += -mcpu=cortex-m3
ASFLAGS += -mthumb

CFLAGS += -mcpu=cortex-m3
CFLAGS += -specs=nano.specs
CFLAGS += -mthumb
CFLAGS += -g
CFLAGS += -O2
CFLAGS += -fno-common

CFLAGS += -I./Inc
CFLAGS += -I./Src
CFLAGS += -I./Drivers/STM32F1xx_HAL_Driver/Inc/
CFLAGS += -I./Drivers/CMSIS/Device/ST/STM32F1xx/Include
CFLAGS += -I./Drivers/CMSIS/Include

CFLAGS += -DSTM32F100xB=1

#LSCRIPT = ./ld/stm32.ld
#LSCRIPT = ./ld/arm-gcc-link.ld
LSCRIPT = ./ld/STM32F100XB_FLASH.ld
LDFLAGS += -Wl,-T$(LSCRIPT)

OBJS = Src/main.o Src/stm32f1xx_hal_msp.o Src/stm32f1xx_it.o Src/system_stm32f1xx.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_gpio.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_rcc.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_cortex.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_uart.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_dma.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_spi.o
OBJS += ./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_pwr.o
OBJS += startup_stm32f100xb.o

all: $(TARGET).elf

$(TARGET).elf: $(OBJS)
	@echo
	@echo Linking: $@
	$(LD) $(LDFLAGS) $(CFLAGS) -o $@ $^
	$(OD) -h -S $(TARGET).elf  > $(TARGET).lst

startup_stm32f100xb.o: ./Drivers/CMSIS/Device/ST/STM32F1xx/Source/Templates/gcc/startup_stm32f100xb.s
	$(AS) -I. ./Drivers/CMSIS/Device/ST/STM32F1xx/Source/Templates/gcc/startup_stm32f100xb.s -o startup_stm32f100xb.o

main.o: src/main.c
	@echo
	@echo Compiling: $<
	$(CC) -c $(CFLAGS) -I. src/main.c -o src/main.o

%.o: inc/%.c
	@echo
	@echo Compiling: $<
	$(CC) -c $(CFLAGS) -I. $< -o inc/$@

%.o: inc/%.S
	@echo
	@echo Assembling: $<
	$(AS) $(ASFLAGS) -o inc/$@ $< -alh=inc/$*.lst

clean:
	@echo
	@echo Cleaning:
	$(RM) $(OBJS)
	$(RM) *.o
	$(RM) src/*.o
	$(RM) inc/*.o
	$(RM) *.elf
	$(RM) *.lst

upload:
	openocd -f ./openocd_rs41.cfg -c "program $(TARGET).elf verify reset exit"
