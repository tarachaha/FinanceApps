using AutoMapper;
using FinanceASP.NETCore.Dtos;
using FinanceASP.NETCore.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace FinanceASP.NETCore.Helpers
{
    public class AutoMapperProfiles : Profile
    {
        public AutoMapperProfiles()
        {
            CreateMap<User, UserForLoginDto>();
            CreateMap<User, UserForRegisterDto>();
            CreateMap<User, UserMinimalInfoDto>();
        }
    }
}
